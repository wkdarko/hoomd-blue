// Copyright (c) 2009-2022 The Regents of the University of Michigan.
// Part of HOOMD-blue, released under the BSD 3-Clause License.

#include "TriangleAreaConservationMeshForceCompute.h"

#include <iostream>
#include <math.h>
#include <sstream>
#include <stdexcept>

using namespace std;

// SMALL a relatively small number
#define SMALL Scalar(0.001)

/*! \file MeshTriangleAreaConservationForceCompute.cc
    \brief Contains code for the MeshTriangleAreaConservationForceCompute class
*/

namespace hoomd
    {
namespace md
    {
/*! \param sysdef System to compute forces on
    \post Memory is allocated, and forces are zeroed.
*/
TriangleAreaConservationMeshForceCompute::TriangleAreaConservationMeshForceCompute(
    std::shared_ptr<SystemDefinition> sysdef,
    std::shared_ptr<MeshDefinition> meshdef)
    : ForceCompute(sysdef), m_K(NULL), m_Amesh(NULL), m_mesh_data(meshdef)
    {
    m_exec_conf->msg->notice(5) << "Constructing TriangleAreaConservationhMeshForceCompute" << endl;

    // allocate the parameters
    m_K = new Scalar[m_pdata->getNTypes()];
    m_Amesh = new Scalar[m_pdata->getNTypes()];
    }

TriangleAreaConservationMeshForceCompute::~TriangleAreaConservationMeshForceCompute()
    {
    m_exec_conf->msg->notice(5) << "Destroying TriangleAreaConservationMeshForceCompute" << endl;

    delete[] m_K;
    delete[] m_Amesh;
    m_K = NULL;
    m_Amesh = NULL;
    }

/*! \param type Type of the angle to set parameters for
    \param K Stiffness parameter for the force computation
    \param A_mesh desired surface area to maintain for the force computation

    Sets parameters for the potential of a particular angle type
*/
void TriangleAreaConservationMeshForceCompute::setParams(unsigned int type, Scalar K, Scalar A_mesh)
    {
    m_K[type] = K;
    m_Amesh[type] = A_mesh;

    // check for some silly errors a user could make
    if (K <= 0)
        m_exec_conf->msg->warning() << "TriangleAreaConservation: specified K <= 0" << endl;

    if (A_mesh <= 0)
        m_exec_conf->msg->warning() << "TriangleAreaConservation: specified A_mesh <= 0" << endl;
    }

void TriangleAreaConservationMeshForceCompute::setParamsPython(std::string type,
                                                               pybind11::dict params)
    {
    auto typ = m_mesh_data->getMeshTriangleData()->getTypeByName(type);
    auto _params = triangle_area_conservation_params(params);
    setParams(typ, _params.k, _params.A_mesh);
    }

pybind11::dict TriangleAreaConservationMeshForceCompute::getParams(std::string type)
    {
    auto typ = m_mesh_data->getMeshTriangleData()->getTypeByName(type);
    if (typ >= m_mesh_data->getMeshTriangleData()->getNTypes())
        {
        m_exec_conf->msg->error() << "mesh.area_conservation: Invalid mesh type specified" << endl;
        throw runtime_error("Error setting parameters in TriangleAreaConservationMeshForceCompute");
        }
    pybind11::dict params;
    params["k"] = m_K[typ];
    params["A_mesh"] = m_Amesh[typ];
    return params;
    }

/*! Actually perform the force computation
    \param timestep Current time step
 */
void TriangleAreaConservationMeshForceCompute::computeForces(uint64_t timestep)
    {
    if (m_prof)
        m_prof->push("Triangle Area Conservation in Mesh");

    assert(m_pdata);
    // access the particle data arrays
    ArrayHandle<Scalar4> h_pos(m_pdata->getPositions(), access_location::host, access_mode::read);

    ArrayHandle<unsigned int> h_rtag(m_pdata->getRTags(), access_location::host, access_mode::read);

    ArrayHandle<Scalar4> h_force(m_force, access_location::host, access_mode::overwrite);
    ArrayHandle<Scalar> h_virial(m_virial, access_location::host, access_mode::overwrite);
    size_t virial_pitch = m_virial.getPitch();

    ArrayHandle<typename MeshTriangle::members_t> h_triangles(
        m_mesh_data->getMeshTriangleData()->getMembersArray(),
        access_location::host,
        access_mode::read);

    // there are enough other checks on the input data: but it doesn't hurt to be safe
    assert(h_force.data);
    assert(h_virial.data);
    assert(h_pos.data);
    assert(h_rtag.data);
    assert(h_triangles.data);

    // Zero data for force calculation.
    memset((void*)h_force.data, 0, sizeof(Scalar4) * m_force.getNumElements());
    memset((void*)h_virial.data, 0, sizeof(Scalar) * m_virial.getNumElements());

    // get a local copy of the simulation box too
    const BoxDim& box = m_pdata->getGlobalBox();

    PDataFlags flags = m_pdata->getFlags();
    bool compute_virial = flags[pdata_flag::pressure_tensor];

    Scalar triangle_area_conservation_virial[6];
    for (unsigned int i = 0; i < 6; i++)
        triangle_area_conservation_virial[i] = Scalar(0.0);

    // for each of the triangles
    const unsigned int size = (unsigned int)m_mesh_data->getMeshTriangleData()->getN();

    // from whole surface area A_mesh to the surface of individual triangle A_mesh -> At
    Scalar At = m_Amesh[0] / size;

    m_area = 0;

    for (unsigned int i = 0; i < size; i++)
        {
        // lookup the tag of each of the particles participating in the triangle
        const typename MeshTriangle::members_t& triangle = h_triangles.data[i];
        assert(triangle.tag[0] < m_pdata->getMaximumTag() + 1);
        assert(triangle.tag[1] < m_pdata->getMaximumTag() + 1);
        assert(triangle.tag[2] < m_pdata->getMaximumTag() + 1);

        // transform a, b, and c into indices into the particle data arrays
        // (MEM TRANSFER: 4 integers)
        unsigned int idx_a = h_rtag.data[triangle.tag[0]];
        unsigned int idx_b = h_rtag.data[triangle.tag[1]];
        unsigned int idx_c = h_rtag.data[triangle.tag[2]];

        assert(idx_a < m_pdata->getN() + m_pdata->getNGhosts());
        assert(idx_b < m_pdata->getN() + m_pdata->getNGhosts());
        assert(idx_c < m_pdata->getN() + m_pdata->getNGhosts());

        // calculate d\vec{r}
        Scalar3 dab;
        dab.x = h_pos.data[idx_b].x - h_pos.data[idx_a].x;
        dab.y = h_pos.data[idx_b].y - h_pos.data[idx_a].y;
        dab.z = h_pos.data[idx_b].z - h_pos.data[idx_a].z;

        Scalar3 dac;
        dac.x = h_pos.data[idx_c].x - h_pos.data[idx_a].x;
        dac.y = h_pos.data[idx_c].y - h_pos.data[idx_a].y;
        dac.z = h_pos.data[idx_c].z - h_pos.data[idx_a].z;

        // apply minimum image conventions to all 3 vectors
        dab = box.minImage(dab);
        dac = box.minImage(dac);

        Scalar3 da, db, dc;
        da.x = h_pos.data[idx_a].x;
        da.y = h_pos.data[idx_a].y;
        da.z = h_pos.data[idx_a].z;
        db.x = h_pos.data[idx_b].x;
        db.y = h_pos.data[idx_b].y;
        db.z = h_pos.data[idx_b].z;
        dc.x = h_pos.data[idx_c].x;
        dc.y = h_pos.data[idx_c].y;
        dc.z = h_pos.data[idx_c].z;

        // FLOPS: 14 / MEM TRANSFER: 2 Scalars

        // FLOPS: 42 / MEM TRANSFER: 6 Scalars
        Scalar rsqab = dab.x * dab.x + dab.y * dab.y + dab.z * dab.z;
        Scalar rsqac = dac.x * dac.x + dac.y * dac.y + dac.z * dac.z;

        Scalar rabrac = dab.x * dac.x + dab.y * dac.y + dab.z * dac.z;

        Scalar area2 = sqrt(rsqab * rsqac - rabrac * rabrac);

        Scalar prefactor = -m_K[0] / (2 * At * area2) * (area2 / 2 - At);

        Scalar energy_pp = m_K[0] / (6.0 * At) * (area2 / 2 - At) * (area2 / 2 - At);

        m_area += area2 / 2;

        Scalar3 Fa, Fb, Fc;
        Fa = prefactor * ((rabrac - rsqac) * dab + (rabrac - rsqab) * dac);
        Fb = prefactor * (rsqac * dab - rabrac * dac);
        Fc = prefactor * (rsqab * dac - rabrac * dab);

        if (compute_virial)
            {
            triangle_area_conservation_virial[0] = Scalar(1. / 2.) * da.x * Fa.x; // xx
            triangle_area_conservation_virial[1] = Scalar(1. / 2.) * da.y * Fa.x; // xy
            triangle_area_conservation_virial[2] = Scalar(1. / 2.) * da.z * Fa.x; // xz
            triangle_area_conservation_virial[3] = Scalar(1. / 2.) * da.y * Fa.y; // yy
            triangle_area_conservation_virial[4] = Scalar(1. / 2.) * da.z * Fa.y; // yz
            triangle_area_conservation_virial[5] = Scalar(1. / 2.) * da.z * Fa.z; // zz
            }

        // Now, apply the force to each individual atom a,b,c, and accumulate the energy/virial
        // do not update ghost particles
        if (idx_a < m_pdata->getN())
            {
            h_force.data[idx_a].x += Fa.x;
            h_force.data[idx_a].y += Fa.y;
            h_force.data[idx_a].z += Fa.z;
            h_force.data[idx_a].w += energy_pp; // divided by 3 because of three
                                                                    // particles sharing the energy

            for (int j = 0; j < 6; j++)
                h_virial.data[j * virial_pitch + idx_a] += triangle_area_conservation_virial[j];
            }

        if (compute_virial)
            {
            triangle_area_conservation_virial[0] = Scalar(1. / 2.) * db.x * Fb.x; // xx
            triangle_area_conservation_virial[1] = Scalar(1. / 2.) * db.y * Fb.x; // xy
            triangle_area_conservation_virial[2] = Scalar(1. / 2.) * db.z * Fb.x; // xz
            triangle_area_conservation_virial[3] = Scalar(1. / 2.) * db.y * Fb.y; // yy
            triangle_area_conservation_virial[4] = Scalar(1. / 2.) * db.z * Fb.y; // yz
            triangle_area_conservation_virial[5] = Scalar(1. / 2.) * db.z * Fb.z; // zz
            }

        if (idx_b < m_pdata->getN())
            {
            h_force.data[idx_b].x += Fb.x;
            h_force.data[idx_b].y += Fb.y;
            h_force.data[idx_b].z += Fb.z;
            h_force.data[idx_b].w += energy_pp;
            for (int j = 0; j < 6; j++)
                h_virial.data[j * virial_pitch + idx_b] += triangle_area_conservation_virial[j];
            }

        if (compute_virial)
            {
            triangle_area_conservation_virial[0] = Scalar(1. / 2.) * dc.x * Fc.x; // xx
            triangle_area_conservation_virial[1] = Scalar(1. / 2.) * dc.y * Fc.x; // xchy
            triangle_area_conservation_virial[2] = Scalar(1. / 2.) * dc.z * Fc.x; // xz
            triangle_area_conservation_virial[3] = Scalar(1. / 2.) * dc.y * Fc.y; // yy
            triangle_area_conservation_virial[4] = Scalar(1. / 2.) * dc.z * Fc.y; // yz
            triangle_area_conservation_virial[5] = Scalar(1. / 2.) * dc.z * Fc.z; // zz
            }

        if (idx_c < m_pdata->getN())
            {
            h_force.data[idx_c].x += Fc.x;
            h_force.data[idx_c].y += Fc.y;
            h_force.data[idx_c].z += Fc.z;
            h_force.data[idx_c].w += energy_pp;
            for (int j = 0; j < 6; j++)
                h_virial.data[j * virial_pitch + idx_c] += triangle_area_conservation_virial[j];
            }
        }

    if (m_prof)
        m_prof->pop();
    }

Scalar TriangleAreaConservationMeshForceCompute::energyDiff(unsigned int idx_a,
                                                            unsigned int idx_b,
                                                            unsigned int idx_c,
                                                            unsigned int idx_d,
                                                            unsigned int type_id)
    {
    ArrayHandle<Scalar4> h_pos(m_pdata->getPositions(), access_location::host, access_mode::read);

    const BoxDim& box = m_pdata->getGlobalBox();

    // calculate d\vec{r}
    Scalar3 dab;
    dab.x = h_pos.data[idx_b].x - h_pos.data[idx_a].x;
    dab.y = h_pos.data[idx_b].y - h_pos.data[idx_a].y;
    dab.z = h_pos.data[idx_b].z - h_pos.data[idx_a].z;

    Scalar3 dac;
    dac.x = h_pos.data[idx_c].x - h_pos.data[idx_a].x;
    dac.y = h_pos.data[idx_c].y - h_pos.data[idx_a].y;
    dac.z = h_pos.data[idx_c].z - h_pos.data[idx_a].z;

    Scalar3 dbd;
    dbd.x = h_pos.data[idx_d].x - h_pos.data[idx_b].x;
    dbd.y = h_pos.data[idx_d].y - h_pos.data[idx_b].y;
    dbd.z = h_pos.data[idx_d].z - h_pos.data[idx_b].z;

    Scalar3 ddc;
    ddc.x = h_pos.data[idx_c].x - h_pos.data[idx_d].x;
    ddc.y = h_pos.data[idx_c].y - h_pos.data[idx_d].y;
    ddc.z = h_pos.data[idx_c].z - h_pos.data[idx_d].z;

    // apply minimum image conventions to all 3 vectors
    dab = box.minImage(dab);
    dac = box.minImage(dac);
    dbd = box.minImage(dbd);
    ddc = box.minImage(ddc);

    Scalar rab = sqrt(dab.x * dab.x + dab.y * dab.y + dab.z * dab.z);
    Scalar rac = sqrt(dac.x * dac.x + dac.y * dac.y + dac.z * dac.z);
    Scalar rbd = sqrt(dbd.x * dbd.x + dbd.y * dbd.y + dbd.z * dbd.z);
    Scalar rdc = sqrt(ddc.x * ddc.x + ddc.y * ddc.y + ddc.z * ddc.z);

    Scalar3 nab = dab / rab;
    Scalar3 nac = dac / rac;
    Scalar3 nbd = dbd / rbd;
    Scalar3 ndc = ddc / rdc;

    Scalar c_baac = nab.x * nac.x + nab.y * nac.y + nab.z * nac.z;
    if (c_baac > 1.0)
        c_baac = 1.0;
    if (c_baac < -1.0)
        c_baac = -1.0;

    Scalar c_abbd = -(nab.x * nbd.x + nab.y * nbd.y + nab.z * nbd.z);
    if (c_abbd > 1.0)
        c_abbd = 1.0;
    if (c_abbd < -1.0)
        c_abbd = -1.0;

    Scalar c_dcca = ndc.x * nac.x + ndc.y * nac.y + ndc.z * nac.z;
    if (c_dcca > 1.0)
        c_dcca = 1.0;
    if (c_dcca < -1.0)
        c_dcca = -1.0;

    Scalar c_bddc = -(ndc.x * nbd.x + ndc.y * nbd.y + ndc.z * nbd.z);
    if (c_bddc > 1.0)
        c_bddc = 1.0;
    if (c_bddc < -1.0)
        c_bddc = -1.0;

    Scalar s_baac = sqrt(1.0 - c_baac * c_baac);
    Scalar s_abbd = sqrt(1.0 - c_abbd * c_abbd);
    Scalar s_dcca = sqrt(1.0 - c_dcca * c_dcca);
    Scalar s_bddc = sqrt(1.0 - c_bddc * c_bddc);

    Scalar energy_old1 = rab * rac * s_baac / 2.0 - m_Amesh[type_id];
    Scalar energy_old2 = rab * rbd * s_abbd / 2.0 - m_Amesh[type_id];

    Scalar energy_new1 = rac * rdc * s_dcca / 2.0 - m_Amesh[type_id];
    Scalar energy_new2 = rdc * rbd * s_bddc / 2.0 - m_Amesh[type_id];

    return m_K[0] / (2.0 * m_Amesh[0])
           * (energy_new1 * energy_new1 + energy_new2 * energy_new2 - energy_old1 * energy_old1
              - energy_old2 * energy_old2);
    }

namespace detail
    {
void export_TriangleAreaConservationMeshForceCompute(pybind11::module& m)
    {
    pybind11::class_<TriangleAreaConservationMeshForceCompute,
                     ForceCompute,
                     std::shared_ptr<TriangleAreaConservationMeshForceCompute>>(
        m,
        "TriangleAreaConservationMeshForceCompute")
        .def(pybind11::init<std::shared_ptr<SystemDefinition>, std::shared_ptr<MeshDefinition>>())
        .def("setParams", &TriangleAreaConservationMeshForceCompute::setParamsPython)
        .def("getParams", &TriangleAreaConservationMeshForceCompute::getParams)
        .def("getArea", &TriangleAreaConservationMeshForceCompute::getArea);
    }

    } // end namespace detail
    } // end namespace md
    } // end namespace hoomd
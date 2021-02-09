# Copyright (c) 2009-2021 The Regents of the University of Michigan
# This file is part of the HOOMD-blue project, released under the BSD 3-Clause License.

""" Compute properties of hard particle configurations.
"""

from __future__ import print_function

from hoomd import _hoomd
from hoomd.operation import Compute
from hoomd.hpmc import _hpmc
from hoomd.hpmc import integrate
from hoomd.data.parameterdicts import ParameterDict
from hoomd.data.typeconverter import Either, to_type_converter
from hoomd.logging import log
import hoomd

class FreeVolume(Compute):
    R""" Compute the free volume available to a test particle by stochastic integration.

    Args:
        mc (:py:mod:`hoomd.hpmc.integrate.HPMCIntegrator`): MC integrator.
        seed (int): Random seed for MC integration.
        type (str): Type of particle to use for integration
        nsample (int): Number of samples to use in MC integration
        suffix (str): Suffix to use for log quantity

    :py:class`FreeVolume` computes the free volume of a particle assembly using stochastic integration with a test particle type.
    It works together with an HPMC integrator, which defines the particle types used in the simulation.
    As parameters it requires the number of MC integration samples (*nsample*), and the type of particle (*test_type*)
    to use for the integration.

    A :py:class`FreeVolume` object can be added to a logger for logging during a simulation,
    see :py:class:`hoomd.logging.Logger` for more details.

    Examples::

        mc = hoomd.hpmc.integrate.Sphere(seed=415236)
        mc.shape["A"] = {'diameter': 1.0}
        mc.shape["B"] = {'diameter': 0.2}
        mc.depletant_fugacity["B"] = 1.5
        fv = hoomd.hpmc.compute.FreeVolume(mc=mc, seed=123, test_type='B', nsample=1000)

    """
    def __init__(self, mc, seed, test_type=None, nsample=None, suffix=''):
        if suffix != '':
            suffix = '_' + suffix
        # store metadata
        param_dict = ParameterDict(
            mc=integrate.HPMCIntegrator,
            seed=int,
            suffix=str,
            test_particle_type=Either([to_type_converter(str),
                                      to_type_converter(int)]),
            num_samples=int
        )
        param_dict.update(
            dict(mc=mc,
                 seed=int(seed),
                 suffix=str(suffix),
                 test_particle_type=str(test_type),
                 num_samples=int(nsample)))
        # set defaults
        self._param_dict.update(param_dict)

    def _attach(self):
        self.test_particle_type = self._simulation.state._cpp_sys_def.getParticleData().getTypeByName(self.test_particle_type)
        # create the c++ mirror class
        cls = None
        if isinstance(self._simulation.device, hoomd.device.CPU):
            if isinstance(self.mc, integrate.Sphere):
                cls = _hpmc.ComputeFreeVolumeSphere
            elif isinstance(self.mc, integrate.ConvexPolygon):
                cls = _hpmc.ComputeFreeVolumeConvexPolygon
            elif isinstance(self.mc, integrate.SimplePolygon):
                cls = _hpmc.ComputeFreeVolumeSimplePolygon
            elif isinstance(self.mc, integrate.ConvexPolyhedron):
                cls = _hpmc.ComputeFreeVolumeConvexPolyhedron
            elif isinstance(self.mc, integrate.ConvexSpheropolyhedron):
                cls = _hpmc.ComputeFreeVolumeSpheropolyhedron
            elif isinstance(self.mc, integrate.Ellipsoid):
                cls = _hpmc.ComputeFreeVolumeEllipsoid
            elif isinstance(self.mc, integrate.ConvexSpheropolygon):
                cls = _hpmc.ComputeFreeVolumeSpheropolygon
            elif isinstance(self.mc, integrate.FacetedEllipsoid):
                cls = _hpmc.ComputeFreeVolumeFacetedEllipsoid
            elif isinstance(self.mc, integrate.Polyhedron):
                cls = _hpmc.ComputeFreeVolumePolyhedron
            elif isinstance(self.mc, integrate.Sphinx):
                cls = _hpmc.ComputeFreeVolumeSphinx
            elif isinstance(self.mc, integrate.ConvexSpheropolyhedronUnion):
                cls = _hpmc.ComputeFreeVolumeConvexPolyhedronUnion
            elif isinstance(self.mc, integrate.FacetedEllipsoidUnion):
                cls = _hpmc.ComputeFreeVolumeFacetedEllipsoidUnion
            elif isinstance(self.mc, integrate.SphereUnion):
                cls = _hpmc.ComputeFreeVolumeSphereUnion
            else:
                raise RuntimeError("compute.free_volume: Unsupported integrator.\n")
        else:
            if isinstance(self.mc, integrate.Sphere):
                cls = _hpmc.ComputeFreeVolumeGPUSphere
            elif isinstance(self.mc, integrate.ConvexPolygon):
                cls = _hpmc.ComputeFreeVolumeGPUConvexPolygon
            elif isinstance(self.mc, integrate.SimplePolygon):
                cls = _hpmc.ComputeFreeVolumeGPUSimplePolygon
            elif isinstance(self.mc, integrate.ConvexPolyhedron):
                cls = _hpmc.ComputeFreeVolumeGPUConvexPolyhedron
            elif isinstance(self.mc, integrate.ConvexSpheropolyhedron):
                cls = _hpmc.ComputeFreeVolumeGPUSpheropolyhedron
            elif isinstance(self.mc, integrate.Ellipsoid):
                cls = _hpmc.ComputeFreeVolumeGPUEllipsoid
            elif isinstance(self.mc, integrate.ConvexSpheropolygon):
                cls = _hpmc.ComputeFreeVolumeGPUSpheropolygon
            elif isinstance(self.mc, integrate.FacetedEllipsoid):
                cls = _hpmc.ComputeFreeVolumeGPUFacetedEllipsoid
            elif isinstance(self.mc, integrate.Polyhedron):
                cls = _hpmc.ComputeFreeVolumeGPUPolyhedron
            elif isinstance(self.mc, integrate.Sphinx):
                cls = _hpmc.ComputeFreeVolumeGPUSphinx
            elif isinstance(self.mc, integrate.SphereUnion):
                cls = _hpmc.ComputeFreeVolumeGPUSphereUnion
            elif isinstance(self.mc, integrate.FacetedEllipsoidUnion):
                cls = _hpmc.ComputeFreeVolumeGPUFacetedEllipsoidUnion
            elif isinstance(self.mc, integrate.ConvexSpheropolyhedronUnion):
                cls = _hpmc.ComputeFreeVolumeGPUConvexPolyhedronUnion
            else:
                raise RuntimeError("compute.free_volume: Unsupported integrator.\n")

        self._cpp_obj = cls(self._simulation.state._cpp_sys_def,
                            self.mc._cpp_obj,
                            _hoomd.CellList(self._simulation.state._cpp_sys_def),
                            self.seed,
                            self.suffix)

        super()._attach()

    @log
    def free_volume(self):
        """free volume available to a particle assembly
        """
        if self._attached:
            return self._cpp_obj.getFreeVolume(self._simulation.timestep)
        else:
            return None

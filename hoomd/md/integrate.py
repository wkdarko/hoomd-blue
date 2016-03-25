# -- start license --
# Highly Optimized Object-oriented Many-particle Dynamics -- Blue Edition
# (HOOMD-blue) Open Source Software License Copyright 2009-2016 The Regents of
# the University of Michigan All rights reserved.

# HOOMD-blue may contain modifications ("Contributions") provided, and to which
# copyright is held, by various Contributors who have granted The Regents of the
# University of Michigan the right to modify and/or distribute such Contributions.

# You may redistribute, use, and create derivate works of HOOMD-blue, in source
# and binary forms, provided you abide by the following conditions:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions, and the following disclaimer both in the code and
# prominently in any materials provided with the distribution.

# * Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions, and the following disclaimer in the documentation and/or
# other materials provided with the distribution.

# * All publications and presentations based on HOOMD-blue, including any reports
# or published results obtained, in whole or in part, with HOOMD-blue, will
# acknowledge its use according to the terms posted at the time of submission on:
# http://codeblue.umich.edu/hoomd-blue/citations.html

# * Any electronic documents citing HOOMD-Blue will link to the HOOMD-Blue website:
# http://codeblue.umich.edu/hoomd-blue/

# * Apart from the above required attributions, neither the name of the copyright
# holder nor the names of HOOMD-blue's contributors may be used to endorse or
# promote products derived from this software without specific prior written
# permission.

# Disclaimer

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND/OR ANY
# WARRANTIES THAT THIS SOFTWARE IS FREE OF INFRINGEMENT ARE DISCLAIMED.

# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -- end license --

# Maintainer: joaander / All Developers are free to add commands for new features

## \package hoomd.integrate
# \brief Commands that integrate the equations of motion
#
# To integrate the system forward in time, an integration mode must be set. Only one integration mode can be active at
# a time, and the last \c integrate.mode_* command before the run() command is the one that will take effect. It is
# possible to set one mode, run() for a certain number of steps and then switch to another mode before the next run()
# command.
#
# The most commonly used mode is integrate.mode_standard . It specifies a standard mode where, at each time
# step, all of the specified forces are evaluated and used in moving the system forward to the next step.
# integrate.mode_standard doesn't integrate any particles by itself, one or more compatible integration methods must
# be specified before the run() command. Like commands that specify forces, integration methods are \b persistent and
# remain set until they are disabled (this differs greatly from HOOMD-blue behavior in all versions prior to 0.9.0).
# The benefit and reason for this change is that now multiple integration methods can be specified on different particle
# groups, allowing portions of the system to be fixed, integrated at a different temperature, etc...
#
# To clarify, the following series of commands will run for 1000 time steps in the NVT ensemble and then switch to
# NVE for another 1000 steps.
#
# \code
# all = group.all()
# integrate.mode_standard(dt=0.005)
# nvt = integrate.nvt(group=all, T=1.2, tau=0.5)
# run(1000)
# nvt.disable()
# integrate.nve(group=all)
# run(1000)
# \endcode
#
# For more detailed information on the interaction of integration methods and integration modes, see
# integrate.mode_standard.
#
# Some integrators provide parameters that can be changed between runs.
# In order to access the integrator to change it, it needs to be saved
# in a variable. For example:
# \code
# integrator = integrate.nvt(group=all, T=1.2, tau=0.5)
# run(100)
# integrator.set_params(T=1.0)
# run(100)
# \endcode
# This code snippet runs the first 100 time steps with T=1.2 and the next 100 with T=1.0

from hoomd import _hoomd;
from hoomd.md import _md;
import hoomd;
from hoomd.integrate import _integrator, _integration_method
import copy;
import sys;

## Enables a variety of standard integration methods
#
# integrate.mode_standard performs a standard time step integration technique to move the system forward. At each time
# step, all of the specified forces are evaluated and used in moving the system forward to the next step.
#
# By itself, integrate.mode_standard does nothing. You must specify one or more integration methods to apply to the
# system. Each integration method can be applied to only a specific group of particles enabling advanced simulation
# techniques.
#
# The following commands can be used to specify the integration methods used by integrate.mode_standard.
# - integrate.brownian
# - integrate.langevin
# - integrate.nve
# - integrate.nvt
# - integrate.npt
# - integrate.nph
#
# There can only be one integration mode active at a time. If there are more than one integrate.mode_* commands in
# a hoomd script, only the most recent before a given run() will take effect.
#
# \MPI_SUPPORTED
class mode_standard(_integrator):
    ## Specifies the standard integration mode
    # \param dt Each time step of the simulation run() will advance the real time of the system forward by \a dt (in time units)
    # \param aniso Whether to integrate rotational degrees of freedom (bool), default None (autodetect)
    #
    # \b Examples:
    # \code
    # integrate.mode_standard(dt=0.005)
    # integrator_mode = integrate.mode_standard(dt=0.001)
    # \endcode
    def __init__(self, dt, aniso=None):
        hoomd.util.print_status_line();

        # initialize base class
        _integrator.__init__(self);

        # Store metadata
        self.dt = dt
        self.aniso = aniso
        self.metadata_fields = ['dt', 'aniso']

        # initialize the reflected c++ class
        self.cpp_integrator = _md.IntegratorTwoStep(hoomd.context.current.system_definition, dt);
        self.supports_methods = True;

        hoomd.context.current.system.setIntegrator(self.cpp_integrator);

        hoomd.util.quiet_status();
        if aniso is not None:
            self.set_params(aniso=aniso)
        hoomd.util.unquiet_status();

    ## \internal
    #  \brief Cached set of anisotropic mode enums for ease of access
    _aniso_modes = {
        None: _md.IntegratorAnisotropicMode.Automatic,
        True: _md.IntegratorAnisotropicMode.Anisotropic,
        False: _md.IntegratorAnisotropicMode.Isotropic}

    ## Changes parameters of an existing integration mode
    # \param dt New time step delta (if set) (in time units)
    # \param aniso Anisotropic integration mode (bool), default None (autodetect)
    #
    # To change the parameters of an existing integration mode, you must save it in a variable when it is
    # specified, like so:
    # \code
    # integrator_mode = integrate.mode_standard(dt=5e-3)
    # \endcode
    #
    # \b Examples:
    # \code
    # integrator_mode.set_params(dt=0.007)
    # integrator_mode.set_params(dt=0.005, aniso=False)
    # \endcode
    def set_params(self, dt=None, aniso=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if dt is not None:
            self.dt = dt
            self.cpp_integrator.setDeltaT(dt);

        if aniso is not None:
            if aniso in self._aniso_modes:
                anisoMode = self._aniso_modes[aniso]
            else:
                hoomd.context.msg.error("integrate.mode_standard: unknown anisotropic mode {}.\n".format(aniso));
                raise RuntimeError("Error setting anisotropic integration mode.");
            self.aniso = aniso
            self.cpp_integrator.setAnisotropicMode(anisoMode)

## NVT Integration via the Nos&eacute;-Hoover thermostat
#
# integrate.nvt performs constant volume, constant temperature simulations using the Nos&eacute;-Hoover thermostat,
# using the MTK equations described in Refs. \cite Martyna1994 \cite Martyna1996.
#
# integrate.nvt is an integration method. It must be used in concert with an integration mode. It can be used while
# the following modes are active:
# - integrate.mode_standard
#
# integrate.nvt uses the proper number of degrees of freedom to compute the temperature of the system in both
# 2 and 3 dimensional systems, as long as the number of dimensions is set before the integrate.nvt command
# is specified.
# \MPI_SUPPORTED
class nvt(_integration_method):
    ## Specifies the NVT integration method
    # \param group Group of particles on which to apply this method.
    # \param T Temperature set point for the Nos&eacute;-Hoover thermostat. (in energy units)
    # \param tau Coupling constant for the Nos&eacute;-Hoover thermostat. (in time units)
    #
    # \f$ \tau \f$ is related to the Nos&eacute; mass \f$ Q \f$ by
    # \f[ \tau = \sqrt{\frac{Q}{g k_B T_0}} \f] where \f$ g \f$ is the number of degrees of freedom,
    # and \f$ k_B T_0 \f$ is the set point (\a T above).
    #
    # \a T can be a variant type, allowing for temperature ramps in simulation runs.
    #
    # Internally, a hoomd.compute.thermo is automatically specified and associated with \a group.
    #
    # \b Examples:
    # \code
    # all = group.all()
    # integrate.nvt(group=all, T=1.0, tau=0.5)
    # integrator = integrate.nvt(group=all, tau=1.0, T=0.65)
    # typeA = group.type('A')
    # integrator = integrate.nvt(group=typeA, tau=1.0, T=hoomd.variant.linear_interp([(0, 4.0), (1e6, 1.0)]))
    # \endcode
    def __init__(self, group, T, tau):
        hoomd.util.print_status_line();

        # initialize base class
        _integration_method.__init__(self);

        # setup the variant inputs
        T = hoomd.variant._setup_variant_input(T);

        # create the compute thermo
        # the NVT integrator uses the ComputeThermo in such a way that ComputeThermo stores half-time step
        # values. By assigning a separate ComputeThermo to the integrator, we are still able to log full time step values
        if group is hoomd.context.current.group_all:
            group_copy = copy.copy(group);
            group_copy.name = "__nvt_all";
            hoomd.util.quiet_status();
            thermo = hoomd.compute.thermo(group_copy);
            hoomd.util.unquiet_status();
        else:
            thermo = hoomd.compute._get_unique_thermo(group=group);

        # store metadata
        self.group = group
        self.T = T
        self.tau = tau
        self.metadata_fields = ['group', 'T', 'tau']

        # setup suffix
        suffix = '_' + group.name;

        if not hoomd.context.exec_conf.isCUDAEnabled():
            self.cpp_method = _md.TwoStepNVTMTK(hoomd.context.current.system_definition, group.cpp_group, thermo.cpp_compute, tau, T.cpp_variant, suffix);
        else:
            self.cpp_method = _md.TwoStepNVTMTKGPU(hoomd.context.current.system_definition, group.cpp_group, thermo.cpp_compute, tau, T.cpp_variant, suffix);

        self.cpp_method.validateGroup()

    ## Changes parameters of an existing integrator
    # \param T New temperature (if set) (in energy units)
    # \param tau New coupling constant (if set) (in time units)
    #
    # To change the parameters of an existing integrator, you must save it in a variable when it is
    # specified, like so:
    # \code
    # integrator = integrate.nvt(group=all, tau=1.0, T=0.65)
    # \endcode
    #
    # \b Examples:
    # \code
    # integrator.set_params(tau=0.6)
    # integrator.set_params(tau=0.7, T=2.0)
    # \endcode
    def set_params(self, T=None, tau=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if T is not None:
            # setup the variant inputs
            T = hoomd.variant._setup_variant_input(T);
            self.cpp_method.setT(T.cpp_variant);
            self.T = T

        if tau is not None:
            self.cpp_method.setTau(tau);
            self.tau = tau

## NPT Integration via MTK barostat-thermostat with triclinic unit cell
#
# integrate.npt performs constant pressure, constant temperature simulations, allowing for a fully deformable
# simulation box
#
# The integration method is based on the rigorous Martyna-Tobias-Klein equations of motion for NPT.
# For optimal stability, the update equations leave the phase-space meeasure invariant and are manifestly
# time-reversible.
#
# By default, integrate.npt performs integration in a cubic box under hydrostatic pressure by simultaneously
# rescaling the lengths \a Lx, \a Ly and \a Lz of the simulation box.
#
# integrate.npt can also perform more advanced integration modes. The integration mode
# is specified by a set of \a couplings and by specifying the box degrees of freedom that are put under
# barostat control.
#
# \a Couplings define which diagonal elements of the pressure tensor \f$ P_{\alpha,\beta} \f$
# should be averaged over, so that the corresponding box lengths are rescaled by the same amount.
#
# Valid \a couplings are:<br>
# - \b none (all box lengths are updated independently)
# - \b xy (\a Lx and \a Ly are coupled)
# - \b xz (\a Lx and \a Lz are coupled)
# - \b yz (\a Ly and \a Lz are coupled)
# - \b xyz (\a Lx and \a Ly and \a Lz are coupled)
#
# The default coupling is \b xyz, i.e. the ratios between all box lengths stay constant.
#
# <em>Degrees of freedom</em> of the box specify which lengths and tilt factors of the box should be updated,
# and how particle coordinates and velocities should be rescaled.
#
# Valid keywords for degrees of freedom are:
# - \b x (the box length Lx is updated)
# - \b y (the box length Ly is updated)
# - \b z (the box length Lz is updated)
# - \b xy (the tilt factor xy is updated)
# - \b xz (the tilt factor xz is updated)
# - \b yz (the tilt factor yz is updated)
# - \b all (all elements are updated, equivalent to \b x, \b y, \b z, \b xy, \b xz, and \b yz together)
#
# Any of the six keywords can be combined together. By default, the \b x, \b y, and \b z degrees of freedom
# are updated.
#
# \note If any of the diagonal \a x, \a y, \a z degrees of freedom is not being integrated, pressure tensor components
#       along that direction are not considered for the remaining degrees of freedom.
#
# For example:
# - Specifying \b xyz copulings and \b x, \b y, and \b z degrees of freedom amounts to \a cubic symmetry (default)
# - Specifying \b xy couplings and \b x, \b y, and \b z degrees of freedom amounts to \a tetragonal symmetry.
# - Specifing no couplings and \b all degrees of freedom amounts to a fully deformable \a triclinic unit cell
#
# integrate.npt is an integration method. It must be used in concert with an integration mode. It can be used while
# the following modes are active:
# - integrate.mode_standard
#
# integrate.npt uses the proper number of degrees of freedom to compute the temperature and pressure of the system in
# both 2 and 3 dimensional systems, as long as the number of dimensions is set before the integrate.npt command
# is specified.
#
# For the MTK equations of motion, see:
# \cite Martyna1994
# \cite Tuckerman2006
# \cite Yu2010
# Glaser et. al (2013), to be published
# \MPI_SUPPORTED
class npt(_integration_method):
    ## Specifies the NPT integrator
    # \param group Group of particles on which to apply this method.
    # \param T Temperature set point for the thermostat, not needed if \b nph=True (in energy units)
    # \param P Pressure set point for the barostat (in pressure units)
    # \param tau Coupling constant for the thermostat, not needed if \a nph=True (in time units)
    # \param tauP Coupling constant for the barostat (in time units)
    # \param couple Couplings of diagonal elements of the stress tensor, can be \b "none", \b "xy", \b "xz",\b "yz", or \b "xyz" (default)
    # \param x if \b True, rescale \a Lx and x component of particle coordinates and velocities
    # \param y if \b True, rescale \a Ly and y component of particle coordinates and velocities
    # \param z if \b True, rescale \a Lz and z component of particle coordinates and velocities
    # \param xy if \b True, rescale \a xy tilt factor and x and y components of particle coordinates and velocities
    # \param xz if \b True, rescale \a xz tilt factor and x and z components of particle coordinates and velocities
    # \param yz if \b True, rescale \a yz tilt factor and y and z components of particle coordinates and velocities
    # \param all if \b True, rescale all lengths and tilt factors and components of particle coordinates and velocities
    # \param nph if \b True, integrate without a thermostat, i.e. in the NPH ensemble
    # \param rescale_all if \b True, rescale all particles, not only those in the group
    #
    # Both \a T and \a P can be variant types, allowing for temperature/pressure ramps in simulation runs.
    #
    # \f$ \tau \f$ is related to the Nos&eacute; mass \f$ Q \f$ by
    # \f[ \tau = \sqrt{\frac{Q}{g k_B T_0}} \f] where \f$ g \f$ is the number of degrees of freedom,
    # and \f$ k_B T_0 \f$ is the set point (\a T above).
    #
    # Internally, a hoomd.compute.thermo is automatically specified and associated with \a group.
    #
    # \b Examples:
    # \code
    # integrate.npt(group=all, T=1.0, tau=0.5, tauP=1.0, P=2.0)
    # integrator = integrate.npt(group=all, tau=1.0, T=0.65, tauP = 1.2, P=2.0)
    # # orthorhombic symmetry
    # integrator = integrate.npt(group=all, tau=1.0, T=0.65, tauP = 1.2, P=2.0, couple="none")
    # # tetragonal symmetry
    # integrator = integrate.npt(group=all, tau=1.0, T=0.65, tauP = 1.2, P=2.0, couple="xy")
    # # triclinic symmetry
    # integrator = integrate.npt(group=all, tau=1.0, T=0.65, tauP = 1.2, P=2.0, couple="none", all=True)
    # \endcode
    def __init__(self, group, P, tauP, couple="xyz", x=True, y=True, z=True, xy=False, xz=False, yz=False, all=False, nph=False, T=None, tau=None, rescale_all=None):
        hoomd.util.print_status_line();

        # check the input
        if (T is None or tau is None):
            if nph is False:
                hoomd.context.msg.error("integrate.npt: Need temperature T and thermostat time scale tau.\n");
                raise RuntimeError("Error setting up NPT integration.");
            else:
                # use dummy values
                T=1.0
                tau=1.0

        if len(group) == 0:
            hoomd.context.msg.error("integrate.npt: Need a non-empty group.\n");
            raise RuntimeError("Error setting up NPT integration.");

        # initialize base class
        _integration_method.__init__(self);

        # setup the variant inputs
        T = hoomd.variant._setup_variant_input(T);
        P = hoomd.variant._setup_variant_input(P);

        # create the compute thermo for half time steps
        if group is hoomd.context.current.group_all:
            group_copy = copy.copy(group);
            group_copy.name = "__npt_all";
            hoomd.util.quiet_status();
            thermo_group = hoomd.compute.thermo(group_copy);
            hoomd.util.unquiet_status();
        else:
            thermo_group = hoomd.compute._get_unique_thermo(group=group);

        # create the compute thermo for full time step
        thermo_group_t = hoomd.compute._get_unique_thermo(group=group);

        # need to know if we are running 2D simulations
        twod = (hoomd.context.current.system_definition.getNDimensions() == 2);
        if twod:
            hoomd.context.msg.notice(2, "When running in 2D, z couplings and degrees of freedom are silently ignored.\n");

        # initialize the reflected c++ class
        if twod:
            # silently ignore any couplings that involve z
            if couple == "none":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_none
            elif couple == "xy":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_xy
            elif couple == "xz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_none
            elif couple == "yz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_none
            elif couple == "xyz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_xy
            else:
                hoomd.context.msg.error("Invalid coupling mode\n");
                raise RuntimeError("Error setting up NPT integration.");
        else:
            if couple == "none":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_none
            elif couple == "xy":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_xy
            elif couple == "xz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_xz
            elif couple == "yz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_yz
            elif couple == "xyz":
                cpp_couple = _md.TwoStepNPTMTK.couplingMode.couple_xyz
            else:
                hoomd.context.msg.error("Invalid coupling mode\n");
                raise RuntimeError("Error setting up NPT integration.");

        # set degrees of freedom flags
        # silently ignore z related degrees of freedom when running in 2d
        flags = 0;
        if x or all:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_x
        if y or all:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_y
        if (z or all) and not twod:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_z
        if xy or all:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_xy
        if (xz or all) and not twod:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_xz
        if (yz or all) and not twod:
            flags |= _md.TwoStepNPTMTK.baroFlags.baro_yz

        if not hoomd.context.exec_conf.isCUDAEnabled():
            self.cpp_method = _md.TwoStepNPTMTK(hoomd.context.current.system_definition, group.cpp_group, thermo_group.cpp_compute, thermo_group_t.cpp_compute, tau, tauP, T.cpp_variant, P.cpp_variant, cpp_couple, flags, nph);
        else:
            self.cpp_method = _md.TwoStepNPTMTKGPU(hoomd.context.current.system_definition, group.cpp_group, thermo_group.cpp_compute, thermo_group_t.cpp_compute, tau, tauP, T.cpp_variant, P.cpp_variant, cpp_couple, flags, nph);

        if rescale_all is not None:
            self.cpp_method.setRescaleAll(rescale_all)

        self.cpp_method.validateGroup()

        # store metadata
        self.group  = group
        self.T = T
        self.tau = tau
        self.P = P
        self.tauP = tauP
        self.couple = couple
        self.rescale_all = rescale_all
        self.all = all
        self.x = x
        self.y = y
        self.z = z
        self.xy = xy
        self.xz = xz
        self.yz = yz
        self.nph = nph

    ## Changes parameters of an existing integrator
    # \param T New temperature (if set) (in energy units)
    # \param tau New coupling constant (if set) (in time units)
    # \param P New pressure (if set) (in pressure units)
    # \param tauP New barostat coupling constant (if set) (in time units)
    # \param rescale_all if \b True, rescale all particles, not only those in the group
    #
    # To change the parameters of an existing integrator, you must save it in a variable when it is
    # specified, like so:
    # \code
    # integrator = integrate.npt(tau=1.0, T=0.65)
    # \endcode
    #
    # \b Examples:
    # \code
    # integrator.set_params(tau=0.6)
    # integrator.set_params(dt=3e-3, T=2.0, P=1.0)
    # \endcode
    def set_params(self, T=None, tau=None, P=None, tauP=None, rescale_all=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if T is not None:
            # setup the variant inputs
            T = hoomd.variant._setup_variant_input(T);
            self.T = T
            self.cpp_method.setT(T.cpp_variant);
        if tau is not None:
            self.cpp_method.setTau(tau);
            self.tau = tau
        if P is not None:
            # setup the variant inputs
            P = hoomd.variant._setup_variant_input(P);
            self.cpp_method.setP(P.cpp_variant);
            self.P = P
        if tauP is not None:
            self.cpp_method.setTauP(tauP);
            self.tauP = tauP
        if rescale_all is not None:
            self.cpp_method.setRescaleAll(rescale_all)
            self.rescale_all = rescale_all

    ## \internal
    # \brief Return information about this integration method
    #
    def get_metadata(self):
        # Metadata output involves transforming some variables into human-readable
        # form, so we override get_metadata()
        data = _integration_method.get_metadata(self)
        data['group'] = self.group.name
        if not self.nph:
            data['T'] = self.T
            data['tau'] = self.tau
        data['P'] = self.P
        data['tauP'] = self.tauP

        lengths = ''
        if self.x or self.all:
            lengths += 'x '
        if self.y or self.all:
            lengths += 'y '
        if self.z or self.all:
            lengths += 'z '
        if self.xy or self.all:
            lengths += 'xy '
        if self.xz or self.all:
            lengths += 'xz '
        if self.yz or self.all:
            lengths += 'yz '
        data['lengths'] = lengths.rstrip()
        if self.rescale_all is not None:
            data['rescale_all'] = self.rescale_all

        return data

## NPH Integration via MTK barostat-thermostat with triclinic unit cell
#
# integrate.nph performs constant pressure (NPH) simulations using a Martyna-Tobias-Klein barostat, an
# explicitly reversible and measure-preserving integration scheme. It allows for fully deformable simulation
# cells and uses the same underying integrator as integrate.npt (with \b nph=True).
#
# The available options are identical to those of integrate.npt, except that *T* cannot be specified.
# For further information, refer to the documentation of integrate.npt
#
# \note A time scale \b tau_p for the relaxation of the barostat is required. This is defined as the
#       relaxation time the barostat would have at an average temperature \f$ T_0 =1 \f$, and it
#       is related to the internally used (Andersen) Barostat mass \f$W\f$ via
#       \f$ W=d N T_0 \tau_p^2 \f$, where \f$ d \f$ is the dimensionsality and \f$ N \f$ the number
#       of particles.
#
# integrate.nph is an integration method. It must be used in concert with an integration mode. It can be used while
# the following modes are active:
# - integrate.mode_standard
#
# \sa integrate.npt
# \MPI_SUPPORTED
class nph(npt):
    ## Specifies the NPH integrator
    # \param params Parameters used for the underlying integrate.npt (for documentation, see there)
    #
    # \b Examples:
    # \code
    # # Triclinic unit cell
    # nph=integrate.nph(group=all, P=2.0, tau_p=1.0, couple="none", all=True)
    # # Cubic unit cell
    # nph = integrate.nph(group=all, P=2.0, tau_p=1.0)
    # \endcode
    def __init__(self, **params):
        hoomd.util.print_status_line();

        # initialize base class
        hoomd.util.quiet_status();
        npt.__init__(self, nph=True, T=1.0, **params);
        hoomd.util.unquiet_status();

## NVE Integration via Velocity-Verlet
#
# integrate.nve performs constant volume, constant energy simulations using the standard
# Velocity-Verlet method. For poor initial conditions that include overlapping atoms, a
# limit can be specified to the movement a particle is allowed to make in one time step.
# After a few thousand time steps with the limit set, the system should be in a safe state
# to continue with unconstrained integration.
#
# Another use-case for integrate.nve is to fix the velocity of a certain group of particles. This can be achieved by
# setting the velocity of those particles in the initial condition and setting the \a zero_force option to True
# for that group. A True value for \a zero_force causes integrate.nve to ignore any net force on each particle and
# integrate them forward in time with a constant velocity.
#
# \note With an active limit, Newton's third law is effectively \b not obeyed and the system
# can gain linear momentum. Activate the update.zero_momentum updater during the limited nve
# run to prevent this.
#
# integrate.nve is an integration method. It must be used in concert with an integration mode. It can be used while
# the following modes are active:
# - integrate.mode_standard
# \MPI_SUPPORTED
class nve(_integration_method):
    ## Specifies the NVE integration method
    # \param group Group of particles on which to apply this method.
    # \param limit (optional) Enforce that no particle moves more than a distance of \a limit in a single time step
    # \param zero_force When set to true, particles in the \a group are integrated forward in time with constant
    #                   velocity and any net force on them is ignored.
    #
    # Internally, a hoomd.compute.thermo is automatically specified and associated with \a group.
    #
    # \b Examples:
    # \code
    # all = group.all()
    # integrate.nve(group=all)
    # integrator = integrate.nve(group=all)
    # typeA = group.type('A')
    # integrate.nve(group=typeA, limit=0.01)
    # integrate.nve(group=typeA, zero_force=True)
    # \endcode
    def __init__(self, group, limit=None, zero_force=False):
        hoomd.util.print_status_line();

        # initialize base class
        _integration_method.__init__(self);

        # create the compute thermo
        hoomd.compute._get_unique_thermo(group=group);

        # initialize the reflected c++ class
        if not hoomd.context.exec_conf.isCUDAEnabled():
            self.cpp_method = _md.TwoStepNVE(hoomd.context.current.system_definition, group.cpp_group, False);
        else:
            self.cpp_method = _md.TwoStepNVEGPU(hoomd.context.current.system_definition, group.cpp_group);

        # set the limit
        if limit is not None:
            self.cpp_method.setLimit(limit);

        self.cpp_method.setZeroForce(zero_force);

        self.cpp_method.validateGroup()

        # store metadata
        self.group = group
        self.limit = limit
        self.metadata_fields = ['group', 'limit']

    ## Changes parameters of an existing integrator
    # \param limit (if set) New limit value to set. Removes the limit if limit is False
    # \param zero_force (if set) New value for the zero force option
    #
    # To change the parameters of an existing integrator, you must save it in a variable when it is
    # specified, like so:
    # \code
    # integrator = integrate.nve(group=all)
    # \endcode
    #
    # \b Examples:
    # \code
    # integrator.set_params(limit=0.01)
    # integrator.set_params(limit=False)
    # \endcode
    def set_params(self, limit=None, zero_force=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if limit is not None:
            if limit == False:
                self.cpp_method.removeLimit();
            else:
                self.cpp_method.setLimit(limit);
            self.limit = limit

        if zero_force is not None:
            self.cpp_method.setZeroForce(zero_force);

## Langevin dynamics
#
# integrate.langevin integrates particles forward in time according to the Langevin equations of motion:
# \f[ m \frac{d\vec{v}}{dt} = \vec{F}_\mathrm{C} - \gamma \cdot \vec{v} + \vec{F}_\mathrm{R}, \f]
# \f[ \langle \vec{F}_\mathrm{R} \rangle = 0, \f]
# \f[ \langle |\vec{F}_\mathrm{R}|^2 \rangle = 2 d k_\mathrm{B} T \gamma / \delta t, \f]
# where \f$ \vec{F}_\mathrm{C} \f$ is the force on the particle from all potentials and constraint forces,
# \f$ \gamma \f$ is the drag coefficient, \f$ \vec{v} \f$ is the particle's velocity, \f$ \vec{F}_\mathrm{R} \f$
# is a uniform random force, and \f$ d \f$ is the dimensionality of the system (2 or 3).  The magnitude of
# the random force is chosen via the fluctuation-dissipation theorem
# to be consistent with the specified drag and temperature, \f$ T \f$.
# When \f$ T=0 \f$, the random force \f$ \vec{F}_\mathrm{R}=0 \f$.
#
# Langevin dynamics includes the acceleration term in the Langevin equation and is useful for gently thermalizing
# systems using a small gamma. This assumption is valid when underdamped: \f$ \frac{m}{\gamma} \gg \delta t \f$.
# Use integrate.brownian if your system is not underdamped.
#
# You can specify \f$ \gamma \f$ in two ways. 1) Use set_gamma() to specify it directly, with
# independent values for each particle type in the system. 2) Specify \f$ \lambda \f$ which scales the particle
# diameter to \f$ \gamma = \lambda d_i \f$. The units of \f$ \lambda \f$ are mass / distance / time.
#
# integrate.langevin must be used with integrate.mode_standard.
#
# \MPI_SUPPORTED
class langevin(_integration_method):
    ## Specifies the Langevin dynamics
    # \param group Group of particles to apply this method to.
    # \param T Temperature of the simulation (in energy units).
    # \param seed Random seed to use for generating \f$ \vec{F}_\mathrm{R} \f$.
    # \param dscale Control \f$ \lambda \f$ options. If 0 or False, use \f$ \gamma \f$ values set per type. If non-zero, \f$ \gamma = \lambda d_i \f$.
    # \param tally (optional) If true, the energy exchange between the thermal reservoir and the particles is
    #                         tracked. Total energy conservation can then be monitored by adding
    #                         \b langevin_reservoir_energy_<i>groupname</i> to the logged quantities.
    # \param noiseless_t If set true, there will be no translational noise (random force)
    # \param noiseless_r If set true, there will be no rotational noise (random torque)
    #
    # \a T can be a variant type, allowing for temperature ramps in simulation runs.
    #
    # A hoomd.compute.thermo is automatically created and associated with \a group.
    #
    # \warning When restarting a simulation, the energy of the reservoir will be reset to zero.
    #
    # \b Examples:
    # \code
    # all = group.all();
    # integrator = integrate.langevin(group=all, T=1.0, seed=5)
    # integrator = integrate.langevin(group=all, T=1.0, dscale=1.5, tally=True)
    # typeA = group.type('A');
    # integrator = integrate.langevin(group=typeA, T=hoomd.variant.linear_interp([(0, 4.0), (1e6, 1.0)]), seed=10)
    # \endcode
    def __init__(self, group, T, seed, dscale=False, tally=False, noiseless_t=False, noiseless_r=False):
        hoomd.util.print_status_line();

        # initialize base class
        _integration_method.__init__(self);

        # setup the variant inputs
        T = hoomd.variant._setup_variant_input(T);

        # create the compute thermo
        hoomd.compute._get_unique_thermo(group=group);

        # setup suffix
        suffix = '_' + group.name;

        if dscale is False or dscale == 0:
            use_lambda = False;
        else:
            use_lambda = True;

        # initialize the reflected c++ class
        if not hoomd.context.exec_conf.isCUDAEnabled():
            my_class = _md.TwoStepLangevin;
        else:
            my_class = _md.TwoStepLangevinGPU;

        self.cpp_method = my_class(hoomd.context.current.system_definition,
                                   group.cpp_group,
                                   T.cpp_variant,
                                   seed,
                                   use_lambda,
                                   float(dscale),
                                   noiseless_t,
                                   noiseless_r,
                                   suffix);

        self.cpp_method.setTally(tally);

        self.cpp_method.validateGroup()

        # store metadata
        self.group = group
        self.T = T
        self.seed = seed
        self.dscale = dscale
        self.noiseless_t = noiseless_t
        self.noiseless_r = noiseless_r
        self.metadata_fields = ['group', 'T', 'seed', 'dscale','noiseless_t','noiseless_r']

    ## Change langevin integrator parameters
    # \param T New temperature (if set) (in energy units)
    # \param tally (optional) If true, the energy exchange between the thermal reservoir and the particles is
    #                         tracked. Total energy conservation can then be monitored by adding
    #                         \b langevin_reservoir_energy_<i>groupname</i> to the logged quantities.
    #
    # \b Examples:
    # \code
    # integrator.set_params(T=2.0)
    # integrator.set_params(tally=False)
    # \endcode
    def set_params(self, T=None, tally=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if T is not None:
            # setup the variant inputs
            T = hoomd.variant._setup_variant_input(T);
            self.cpp_method.setT(T.cpp_variant);
            self.T = T

        if tally is not None:
            self.cpp_method.setTally(tally);

    ## Set gamma for a particle type
    # \param a Particle type name
    # \param gamma \f$ \gamma \f$ for particle type \a (in units of force/velocity)
    #
    # set_gamma() sets the coefficient \f$ \gamma \f$ for a single particle type, identified
    # by name. The default is 1.0 if not specified for a type.
    #
    # It is not an error to specify gammas for particle types that do not exist in the simulation.
    # This can be useful in defining a single simulation script for many different types of particles
    # even when some simulations only include a subset.
    #
    # \b Examples:
    # \code
    # bd.set_gamma('A', gamma=2.0)
    # \endcode
    #
    def set_gamma(self, a, gamma):
        hoomd.util.print_status_line();
        self.check_initialization();
        a = str(a);

        ntypes = hoomd.context.current.system_definition.getParticleData().getNTypes();
        type_list = [];
        for i in range(0,ntypes):
            type_list.append(hoomd.context.current.system_definition.getParticleData().getNameByType(i));

        # change the parameters
        for i in range(0,ntypes):
            if a == type_list[i]:
                self.cpp_method.setGamma(i,gamma);

    ## Set gamma_r for a particle type
    # \param a Particle type name
    # \param gamma_r \f$ \gamma_r \f$ for particle type \a (in units of force/velocity)
    #
    # set_gamma_r() sets the coefficient \f$ \gamma_r \f$ for a single particle type, identified
    # by name. The default is 1.0 if not specified for a type. It must be positive or zero, if set
    # zero, it will have no rotational damping or random torque, but still with updates from normal net torque.
    #
    #
    # \b Examples:
    # \code
    # bd.set_gamma_r('A', gamma_r=2.0)
    # \endcode
    #
    def set_gamma_r(self, a, gamma_r):

        if (gamma_r < 0):
            raise ValueError("The gamma_r must be positive or zero (represent no rotational damping or random torque, but with updates)")

        hoomd.util.print_status_line();
        self.check_initialization();

        ntypes = hoomd.context.current.system_definition.getParticleData().getNTypes();
        type_list = [];
        for i in range(0,ntypes):
            type_list.append(hoomd.context.current.system_definition.getParticleData().getNameByType(i));

        # change the parameters
        for i in range(0,ntypes):
            if a == type_list[i]:
                self.cpp_method.setGamma_r(i,gamma_r);

## Brownian dynamics
#
# integrate.brownian integrates particles forward in time according to the overdamped Langevin equations of motion,
# sometimes called Brownian dynamics, or the diffusive limit.
# \f[ \frac{d\vec{x}}{dt} = \frac{\vec{F}_\mathrm{C} + \vec{F}_\mathrm{R}}{\gamma}, \f]
# \f[ \langle \vec{F}_\mathrm{R} \rangle = 0, \f]
# \f[ \langle |\vec{F}_\mathrm{R}|^2 \rangle = 2 d k_\mathrm{B} T \gamma / \delta t, \f]
# \f[ \langle \vec{v}(t) \rangle = 0, \f]
# \f[ \langle |\vec{v}(t)|^2 \rangle = d k_\mathrm{B} T / m, \f]
# where \f$ \vec{F}_\mathrm{C} \f$ is the force on the particle from all potentials and constraint forces,
# \f$ \gamma \f$ is the drag coefficient, \f$ \vec{F}_\mathrm{R} \f$
# is a uniform random force, \f$ \vec{v} \f$ is the particle's velocity, and \f$ d \f$ is the dimensionality
# of the system. The magnitude of the random force is chosen via the fluctuation-dissipation theorem
# to be consistent with the specified drag and temperature, \f$ T \f$.
# When \f$ T=0 \f$, the random force \f$ \vec{F}_\mathrm{R}=0 \f$.
#
# In Brownian dynamics, particle velocities are completely decoupled from positions. At each time step,
# integrate.brownian draws a new velocity distribution consistent with the current set temperature so that
# hoomd.compute.thermo will report appropriate temperatures if logged or needed by other commands.
#
# Brownian dynamics neglects the acceleration term in the Langevin equation. This assumption is valid when
# overdamped: \f$ \frac{m}{\gamma} \ll \delta t \f$. Use integrate.langevin if your system is not overdamped.
#
# You can specify \f$ \gamma \f$ in two ways. 1) Use set_gamma() to specify it directly, with
# independent values for each particle type in the system. 2) Specify \f$ \lambda \f$ which scales the particle
# diameter to \f$ \gamma = \lambda d_i \f$. The units of \f$ \lambda \f$ are mass / distance / time.
#
# integrate.brownian must be used with integrate.mode_standard.
#
# \MPI_SUPPORTED
class brownian(_integration_method):
    ## Specifies the Brownian dynamics integrator
    # \param group Group of particles to apply this method to.
    # \param T Temperature of the simulation (in energy units).
    # \param seed Random seed to use for generating \f$ \vec{F}_\mathrm{R} \f$.
    # \param dscale Control \f$ \lambda \f$ options. If 0 or False, use \f$ \gamma \f$ values set per type. If non-zero, \f$ \gamma = \lambda d_i \f$.
    # \param noiseless_t If set true, there will be no translational noise (random force)
    # \param noiseless_r If set true, there will be no rotational noise (random torque)
    #
    # \a T can be a variant type, allowing for temperature ramps in simulation runs.
    #
    # A hoomd.compute.thermo is automatically created and associated with \a group.
    #
    # \warning When restarting a simulation, the energy of the reservoir will be reset to zero.
    #
    # \b Examples:
    # \code
    # all = group.all();
    # integrator = integrate.brownian(group=all, T=1.0, seed=5)
    # integrator = integrate.brownian(group=all, T=1.0, dscale=1.5)
    # typeA = group.type('A');
    # integrator = integrate.brownian(group=typeA, T=hoomd.variant.linear_interp([(0, 4.0), (1e6, 1.0)]), seed=10)
    # \endcode
    def __init__(self, group, T, seed, dscale=False, noiseless_t=False, noiseless_r=False):
        hoomd.util.print_status_line();

        # initialize base class
        _integration_method.__init__(self);

        # setup the variant inputs
        T = hoomd.variant._setup_variant_input(T);

        # create the compute thermo
        hoomd.compute._get_unique_thermo(group=group);

        if dscale is False or dscale == 0:
            use_lambda = False;
        else:
            use_lambda = True;

        # initialize the reflected c++ class
        if not hoomd.context.exec_conf.isCUDAEnabled():
            my_class = _md.TwoStepBD;
        else:
            my_class = _md.TwoStepBDGPU;

        self.cpp_method = my_class(hoomd.context.current.system_definition,
                                   group.cpp_group,
                                   T.cpp_variant,
                                   seed,
                                   use_lambda,
                                   float(dscale),
                                   noiseless_t,
                                   noiseless_r);

        self.cpp_method.validateGroup()

        # store metadata
        self.group = group
        self.T = T
        self.seed = seed
        self.dscale = dscale
        self.noiseless_t = noiseless_t
        self.noiseless_r = noiseless_r
        self.metadata_fields = ['group', 'T', 'seed', 'dscale','noiseless_t','noiseless_r']

    ## Change brownian integrator parameters
    # \param T New temperature (if set) (in energy units)
    #
    # \b Examples:
    # \code
    # integrator.set_params(T=2.0)
    # \endcode
    def set_params(self, T=None):
        hoomd.util.print_status_line();
        self.check_initialization();

        # change the parameters
        if T is not None:
            # setup the variant inputs
            T = hoomd.variant._setup_variant_input(T);
            self.cpp_method.setT(T.cpp_variant);
            self.T = T

    ## Set gamma for a particle type
    # \param a Particle type name
    # \param gamma \f$ \gamma \f$ for particle type \a (in units of force/velocity)
    #
    # set_gamma() sets the coefficient \f$ \gamma \f$ for a single particle type, identified
    # by name. The default is 1.0 if not specified for a type.
    #
    # It is not an error to specify gammas for particle types that do not exist in the simulation.
    # This can be useful in defining a single simulation script for many different types of particles
    # even when some simulations only include a subset.
    #
    # \b Examples:
    # \code
    # bd.set_gamma('A', gamma=2.0)
    # \endcode
    #
    def set_gamma(self, a, gamma):
        hoomd.util.print_status_line();
        self.check_initialization();
        a = str(a);

        ntypes = hoomd.context.current.system_definition.getParticleData().getNTypes();
        type_list = [];
        for i in range(0,ntypes):
            type_list.append(hoomd.context.current.system_definition.getParticleData().getNameByType(i));

        # change the parameters
        for i in range(0,ntypes):
            if a == type_list[i]:
                self.cpp_method.setGamma(i,gamma);

    ## Set gamma_r for a particle type
    # \param a Particle type name
    # \param gamma_r \f$ \gamma_r \f$ for particle type \a (in units of force/velocity)
    #
    # set_gamma_r() sets the coefficient \f$ \gamma_r \f$ for a single particle type, identified
    # by name. The default is 1.0 if not specified for a type. The gamma_r must be positive or zero,
    # if set zero, it will ignore any rotational updates (due to singularity).
    #
    # It is not an error to specify gammas for particle types that do not exist in the simulation.
    # This can be useful in defining a single simulation script for many different types of particles
    # even when some simulations only include a subset.
    #
    # \b Examples:
    # \code
    # bd.set_gamma_r('A', gamma_r=2.0)
    # \endcode
    #
    def set_gamma_r(self, a, gamma_r):

        if (gamma_r < 0):
            raise ValueError("The gamma_r must be positive or zero (ignoring any rotational updates)")

        hoomd.util.print_status_line();
        self.check_initialization();

        ntypes = hoomd.context.current.system_definition.getParticleData().getNTypes();
        type_list = [];
        for i in range(0,ntypes):
            type_list.append(hoomd.context.current.system_definition.getParticleData().getNameByType(i));

        # change the parameters
        for i in range(0,ntypes):
            if a == type_list[i]:
                self.cpp_method.setGamma_r(i,gamma_r);

## Energy Minimizer (FIRE)
#
# integrate.mode_minimize_fire uses the Fast Inertial Relaxation Engine (FIRE) algorithm to minimize the energy
# for a group of particles while keeping all other particles fixed.  This method is published in
# Bitzek, et al, PRL, 2006.
#
# At each time step,\f$\Delta t \f$, the algorithm uses the NVE Integrator to generate a x, v, and F, and then adjusts
# v according to \f[ \vec{v} = (1-\alpha)\vec{v} + \alpha \hat{F}|\vec{v}|  \f] where \f$ \alpha \f$ and \f$\Delta t \f$
# are dynamically adaptive quantities.  While a current search has been lowering the energy of system for more than
# \f$N_{min}\f$ steps, \f$ \alpha \f$  is decreased by \f$ \alpha \rightarrow \alpha f_{alpha} \f$ and
# \f$\Delta t \f$ is increased by \f$ \Delta t \rightarrow max(\Delta t * f_{inc}, \Delta t_{max}) \f$.
# If the energy of the system increases (or stays the same), the velocity of the particles is set to 0,
# \f$ \alpha \rightarrow \alpha_{start}\f$ and
# \f$ \Delta t \rightarrow \Delta t * f_{dec} \f$.  Convergence is determined by both the force per particle or the
# change in energy per particle dropping below \a ftol and \a Etol, respectively or,
#
# \f[ \frac{\sum |F|}{N*\sqrt{N_{dof}}} <ftol \;\; and \;\; \Delta \frac{\sum |E|}{N} < Etol  \f]
# where N is the number of particles the minimization is acting over (i.e. the group size).  Either of the two criterion can be effectively turned off by setting the tolerance to a large number.
#
# If the minimization is acted over a subset of all the particles in the system, the "other" particles will be kept
# frozen but will still interact with the particles being moved.
#
# \b Example:
# \code
# fire=integrate.mode_minimize_fire( group=group.all(), dt=0.05, ftol=1e-2, Etol=1e-7)
# while not(fire.has_converged()):
#    xml = dump.xml(filename="dump",period=1)
#    run(100)
# \endcode
#
# \note As a default setting, the algorithm will start with a \f$ \Delta t = \frac{1}{10} \Delta t_{max} \f$ and
# attempts at least 10 search steps.  In practice, it was found that this prevents the simulation from making too
# aggressive a first step, but also from quitting before having found a good search direction. The minimum number of
# attempts can be set by the user.
#
# \warning All other integration methods must be disabled before using the FIRE energy minimizer.
# \MPI_NOT_SUPPORTED
class mode_minimize_fire(_integrator):
    ## Specifies the FIRE energy minimizer.
    # \param group Particle group to be applied FIRE
    # \param group Group of particles on which to apply this method.
    # \param dt This is the maximum step size the minimizer is permitted to use.  Consider the stability of the system when setting. (in time units)
    # \param Nmin Number of steps energy change is negative before allowing \f$ \alpha \f$ and \f$ \Delta t \f$ to adapt.
    #   - <i>optional</i>: defaults to 5
    # \param finc Factor to increase \f$ \Delta t \f$ by
    #   - <i>optional</i>: defaults to 1.1
    # \param fdec Factor to decrease \f$ \Delta t \f$ by
    #   - <i>optional</i>: defaults to 0.5
    # \param alpha_start Initial (and maximum) \f$ \alpha \f$
    #   - <i>optional</i>: defaults to 0.1
    # \param falpha Factor to decrease \f$ \alpha t \f$ by
    #   - <i>optional</i>: defaults to 0.99
    # \param ftol force convergence criteria (in force units)
    #   - <i>optional</i>: defaults to 1e-1
    # \param Etol energy convergence criteria (in energy units)
    #   - <i>optional</i>: defaults to 1e-5
    # \param min_steps A minimum number of attempts before convergence criteria are considered
    #   - <i>optional</i>: defaults to 10
    def __init__(self, group, dt, Nmin=None, finc=None, fdec=None, alpha_start=None, falpha=None, ftol = None, Etol= None, min_steps=None):
        hoomd.util.print_status_line();

        # Error out in MPI simulations
        if (_hoomd.is_MPI_available()):
            if hoomd.context.current.system_definition.getParticleData().getDomainDecomposition():
                hoomd.context.msg.error("mode_minimize_fire is not supported in multi-processor simulations.\n\n")
                raise RuntimeError("Error setting up integration mode.")

        # initialize base class
        _integrator.__init__(self);

        # initialize the reflected c++ class
        if not hoomd.context.exec_conf.isCUDAEnabled():
            self.cpp_integrator = _md.FIREEnergyMinimizer(hoomd.context.current.system_definition, group.cpp_group, dt);
        else:
            self.cpp_integrator = _md.FIREEnergyMinimizerGPU(hoomd.context.current.system_definition, group.cpp_group, dt);

        self.supports_methods = False;

        hoomd.context.current.system.setIntegrator(self.cpp_integrator);

        # change the set parameters if not None
        self.dt = dt
        self.metadata_fields = ['dt']
        if not(Nmin is None):
            self.cpp_integrator.setNmin(Nmin);
            self.Nmin = Nmin
            self.metadata_fields.append('Nmin')
        if not(finc is None):
            self.cpp_integrator.setFinc(finc);
            self.finc = finc
            self.metadata_fields.append('finc')
        if not(fdec is None):
            self.cpp_integrator.setFdec(fdec);
            self.fdec = fdec
            self.metadata_fields.append('fdec')
        if not(alpha_start is None):
            self.cpp_integrator.setAlphaStart(alpha_start);
            self.alpha_start = alpha_start
            self.metadata_fields.append('alpha_start')
        if not(falpha is None):
            self.cpp_integrator.setFalpha(falpha);
            self.falpha = falpha
            self.metadata_fields.append(falpha)
        if not(ftol is None):
            self.cpp_integrator.setFtol(ftol);
            self.ftol = ftol
            self.metadata_fields.append(ftol)
        if not(Etol is None):
            self.cpp_integrator.setEtol(Etol);
            self.Etol = Etol
            self.metadata_fields.append(Etol)
        if not(min_steps is None):
            self.cpp_integrator.setMinSteps(min_steps);
            self.min_steps = min_steps
            self.metadata_fields.append(min_steps)

    ## Asks if Energy Minimizer has converged
    #
    def has_converged(self):
        self.check_initialization();
        return self.cpp_integrator.hasConverged()

## Applies the Berendsen thermostat.
#
# integrate.berendsen rescales the velocities of all particles on each time step. The rescaling is performed so that
# the difference in the current temperature from the set point decays exponentially \cite Berendsen1984
# \f[
#     \frac{dT_\mathrm{cur}}{dt} = \frac{T - T_\mathrm{cur}}{\tau}
# \f]
#
# \MPI_NOT_SUPPORTED
class berendsen(_integration_method):
    ## Initialize the Berendsen thermostat.
    # \param group Group to which the Berendsen thermostat will be applied.
    # \param T Temperature of thermostat. (in energy units)
    # \param tau Time constant of thermostat. (in time units)
    #
    def __init__(self, group, T, tau):
        hoomd.util.print_status_line();

        # Error out in MPI simulations
        if (_hoomd.is_MPI_available()):
            if hoomd.context.current.system_definition.getParticleData().getDomainDecomposition():
                hoomd.context.msg.error("integrate.berendsen is not supported in multi-processor simulations.\n\n")
                raise RuntimeError("Error setting up integration method.")

        # initialize base class
        _integration_method.__init__(self);

        # setup the variant inputs
        T = hoomd.variant._setup_variant_input(T);

        # create the compute thermo
        thermo = hoomd.compute._get_unique_thermo(group = group);

        # initialize the reflected c++ class
        if not hoomd.context.exec_conf.isCUDAEnabled():
            self.cpp_method = _md.TwoStepBerendsen(hoomd.context.current.system_definition,
                                                     group.cpp_group,
                                                     thermo.cpp_compute,
                                                     tau,
                                                     T.cpp_variant);
        else:
            self.cpp_method = _md.TwoStepBerendsenGPU(hoomd.context.current.system_definition,
                                                        group.cpp_group,
                                                        thermo.cpp_compute,
                                                        tau,
                                                        T.cpp_variant);

        # store metadata
        self.T = T
        self.tau = tau
        self.metadata_fields = ['T','tau']
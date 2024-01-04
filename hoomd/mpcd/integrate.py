# Copyright (c) 2009-2023 The Regents of the University of Michigan.
# Part of HOOMD-blue, released under the BSD 3-Clause License.

import itertools

import hoomd
from hoomd.data.parameterdicts import ParameterDict
from hoomd.data import syncedlist
from hoomd.data.typeconverter import OnlyTypes
from hoomd.md.integrate import Integrator as _MDIntegrator, _set_synced_list
from hoomd.mpcd import _mpcd
from hoomd.mpcd.collide import CellList, CollisionMethod
from hoomd.mpcd.fill import VirtualParticleFiller
from hoomd.mpcd.stream import StreamingMethod
from hoomd.mpcd.tune import ParticleSorter


@hoomd.logging.modify_namespace(("mpcd", "Integrator"))
class Integrator(_MDIntegrator):
    """MPCD integrator.

    Args:
        dt (float): Integrator time step size :math:`[\mathrm{time}]`.

        methods (Sequence[hoomd.md.methods.Method]): Sequence of integration
          methods. The default value of ``None`` initializes an empty list.

        forces (Sequence[hoomd.md.force.Force]): Sequence of forces applied to
          the particles in the system. The default value of ``None`` initializes
          an empty list.

        integrate_rotational_dof (bool): When True, integrate rotational degrees
          of freedom.

        constraints (Sequence[hoomd.md.constrain.Constraint]): Sequence of
          constraint forces applied to the particles in the system.
          The default value of ``None`` initializes an empty list. Rigid body
          objects (i.e. `hoomd.md.constrain.Rigid`) are not allowed in the
          list.

        rigid (hoomd.md.constrain.Rigid): An object defining the rigid bodies in
          the simulation.

        half_step_hook (hoomd.md.HalfStepHook): Enables the user to perform
            arbitrary computations during the half-step of the integration.

        streaming_method (hoomd.mpcd.stream.StreamingMethod): Streaming method
            for the MPCD solvent.

        collision_method (hoomd.mpcd.collide.CollisionMethod): Collision method
            for the MPCD solvent and any embedded particles.

        solvent_fillers (Sequence[hoomd.mpcd.fill.VirtualParticleFiller]): Solvent
            virtual-particle filler(s).

        solvent_sorter (hoomd.mpcd.tune.ParticleSorter): Tuner for sorting the
            MPCD particles.

    The MPCD `Integrator` enables the MPCD algorithm concurrently with standard
    MD methods.

    In MPCD simulations, ``dt`` defines the amount of time that the system is
    advanced forward every time step. MPCD streaming and collision steps can be
    defined to occur in multiples of ``dt``. In these cases, any MD particle data
    will be updated every ``dt``, while the MPCD particle data is updated
    asynchronously for performance. For example, if MPCD streaming happens every
    5 steps, then the particle data will be updated as follows::

                0     1     2     3     4     5
        MD:     |---->|---->|---->|---->|---->|
        MPCD:   |---------------------------->|

    If the MPCD particle data is accessed via the snapshot interface at time
    step 3, it will actually contain the MPCD particle data for time step 5.
    The MD particles can be read at any time step because their positions
    are updated every step.


    Attributes:
        collision_method (hoomd.mpcd.collide.CollisionMethod): Collision method
            for the MPCD solvent and any embedded particles.

        solvent_fillers (Sequence[hoomd.mpcd.fill.VirtualParticleFiller]): Solvent
            virtual-particle filler(s).

        solvent_sorter (hoomd.mpcd.tune.ParticleSorter): Tuner for sorting the
            MPCD particles (recommended).

        streaming_method (hoomd.mpcd.stream.StreamingMethod): Streaming method
            for the MPCD solvent.

    """

    def __init__(
        self,
        dt,
        integrate_rotational_dof=False,
        forces=None,
        constraints=None,
        methods=None,
        rigid=None,
        half_step_hook=None,
        streaming_method=None,
        collision_method=None,
        solvent_fillers=None,
        solvent_sorter=None,
    ):
        super().__init__(
            dt,
            integrate_rotational_dof,
            forces,
            constraints,
            methods,
            rigid,
            half_step_hook,
        )

        solvent_fillers = [] if solvent_fillers is None else solvent_fillers
        self._solvent_fillers = syncedlist.SyncedList(
            VirtualParticleFiller,
            syncedlist._PartialGetAttr("_cpp_obj"),
            iterable=solvent_fillers,
        )

        self._cell_list = CellList(cell_size=1.0, shift=True)

        param_dict = ParameterDict(
            streaming_method=OnlyTypes(StreamingMethod, allow_none=True),
            collision_method=OnlyTypes(CollisionMethod, allow_none=True),
            solvent_sorter=OnlyTypes(ParticleSorter, allow_none=True),
        )
        param_dict.update(
            dict(
                streaming_method=streaming_method,
                collision_method=collision_method,
                solvent_sorter=solvent_sorter,
            ))
        self._param_dict.update(param_dict)

    @property
    def cell_list(self):
        """hoomd.mpcd.collide.CellList: Collision cell list.

        A `CellList` is automatically created with each `Integrator`
        using typical defaults of cell size 1 and random grid shifting enabled.
        You can change this configuration if desired.

        """
        return self._cell_list

    @property
    def solvent_fillers(self):
        return self._solvent_fillers

    @solvent_fillers.setter
    def solvent_fillers(self, value):
        _set_synced_list(self._solvent_fillers, value)

    @property
    def _children(self):
        children = super()._children
        for child in itertools.chain(self.solvent_fillers):
            children.extend(child._children)
        return children

    def _attach_hook(self):
        self._cell_list._attach(self._simulation)
        if self.streaming_method is not None:
            self.streaming_method._attach(self._simulation)
        if self.collision_method is not None:
            self.collision_method._attach(self._simulation)
        if self.solvent_sorter is not None:
            self.solvent_sorter._attach(self._simulation)

        self._cpp_obj = _mpcd.Integrator(self._simulation.state._cpp_sys_def,
                                         self.dt)
        self._solvent_fillers._sync(self._simulation, self._cpp_obj.fillers)
        self._cpp_obj.cell_list = self._cell_list._cpp_obj

        super(_MDIntegrator, self)._attach_hook()

    def _detach_hook(self):
        self._solvent_fillers._unsync()
        self._cell_list._detach()
        if self.streaming_method is not None:
            self.streaming_method._detach()
        if self.collision_method is not None:
            self.collision_method._detach()
        if self.solvent_sorter is not None:
            self.solvent_sorter._detach()

        super()._detach_hook()

    def _setattr_param(self, attr, value):
        if attr in ("streaming_method", "collision_method", "solvent_sorter"):
            cur_value = getattr(self, attr)
            if value is cur_value:
                return

            if value is not None and value._attached:
                raise ValueError("Cannot attach to multiple integrators.")

            # if already attached, change out which is attached, then set parameter
            if self._attached:
                if cur_value is not None:
                    cur_value._detach()
                if value is not None:
                    value._attach(self._simulation)
            self._param_dict[attr] = value
        else:
            super()._setattr_param(attr, value)

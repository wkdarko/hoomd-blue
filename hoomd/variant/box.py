# Copyright (c) 2009-2023 The Regents of the University of Michigan.
# Part of HOOMD-blue, released under the BSD 3-Clause License.

"""Implement variants that return box parameters as a function of time."""

from hoomd import _hoomd, Box
from hoomd.data.typeconverter import box_preprocessing, variant_preprocessing


class BoxVariant(_hoomd.VectorVariantBox):
    """Box-like vector variant base class.

    `hoomd.variant.box.BoxVariant` provides an interface to length-6 vector
    variants that are valid `hoomd.box.box_like` objects.  The return value of
    the ``__call__`` method returns a length-6 array of scalar values that
    represent the quantities ``Lx``, ``Ly``, ``Lz``, ``xy``, ``xz``, and ``yz``
    of a simulation box.
    """
    pass


class Constant(_hoomd.VectorVariantBoxConstant, BoxVariant):
    """A constant box variant.

    Args:
        box (hoomd.box.box_like): The box.

    `Constant` returns ``[box.Lx, box.Ly, box.Lz, box.xz, box.xz, box.yz]`` at
    all time steps.
    """

    def __init__(self, box):
        box = box_preprocessing(box)
        BoxVariant.__init__(self)
        _hoomd.VectorVariantBoxConstant.__init__(self, box._cpp_obj)

    @property
    def box(self):
        """hoomd.Box: The box."""
        return Box._from_cpp(self._box)

    @box.setter
    def box(self, box):
        box = box_preprocessing(box)
        self._box = box._cpp_obj


class Interpolate(_hoomd.VectorVariantBoxInterpolate, BoxVariant):
    """Interpolate between two boxes linearly.

    Args:
        initial_box (hoomd.box.box_like): The initial box.
        final_box (hoomd.box.box_like): The final box.
        variant (hoomd.variant.variant_like): A variant used to interpolate
            between the two boxes.

    ``Interpolate`` returns arrays corresponding to a linear interpolation between the
    initial and final boxes where the minimum of the variant gives ``initial_box`` and
    the maximum gives ``final_box``:

    .. math::

        \\begin{align*}
        L_{x}' &= \\lambda L_{2x} + (1 - \\lambda) L_{1x} \\\\
        L_{y}' &= \\lambda L_{2y} + (1 - \\lambda) L_{1y} \\\\
        L_{z}' &= \\lambda L_{2z} + (1 - \\lambda) L_{1z} \\\\
        xy' &= \\lambda xy_{2} + (1 - \\lambda) xy_{1} \\\\
        xz' &= \\lambda xz_{2} + (1 - \\lambda) xz_{1} \\\\
        yz' &= \\lambda yz_{2} + (1 - \\lambda) yz_{1} \\\\
        \\end{align*}

    Where ``initial_box`` is :math:`(L_{ix}, L_{iy}, L_{iz}, xy_i, xz_i, yz_i)`,
    ``final_box`` is :math:`(L_{fx}, L_{fy}, L_{fz}, xy_f, xz_f, yz_f)`,
    :math:`\\lambda = \\frac{f(t) - \\min f}{\\max f - \\min f}`, :math:`t`
    is the timestep, and :math:`f(t)` is given by `variant`.

    Attributes:
        variant (hoomd.variant.Variant): A variant used to interpolate between
            the two boxes.
    """

    def __init__(self, initial_box, final_box, variant):
        box1 = box_preprocessing(initial_box)
        box2 = box_preprocessing(final_box)
        variant = variant_preprocessing(variant)
        BoxVariant.__init__(self)
        _hoomd.VectorVariantBoxInterpolate.__init__(self, box1._cpp_obj,
                                                    box2._cpp_obj, variant)

    @property
    def initial_box(self):
        """hoomd.Box: The initial box."""
        return Box._from_cpp(self._initial_box)

    @initial_box.setter
    def initial_box(self, box):
        box = box_preprocessing(box)
        self._initial_box = box._cpp_obj

    @property
    def final_box(self):
        """hoomd.Box: the final box."""
        return Box._from_cpp(self._final_box)

    @final_box.setter
    def final_box(self, box):
        box = box_preprocessing(box)
        self._final_box = box._cpp_obj


class InverseVolumeRamp(_hoomd.VectorVariantBoxInverseVolumeRamp, BoxVariant):
    """Produce box arrays whose inverse volume changes linearly.

    Args:
        initial_box (hoomd.box.box_like): The initial box.
        final_volume (float): The final volume of the box.
        t_start (int): The time step at the start of the ramp.
        t_ramp (int): The length of the ramp.

    ``InverseVolumeRamp`` produces box arrays that correspond to a box whose
    **inverse volume** (i.e., number density for a constant number of particles) varies
    linearly. The shape of the box remains constant, that is, the
    ratios of the lengths of the box vectors (:math:`L_y / L_x` and
    :math:`L_z / L_x`) and the tilt factors (:math:`xy`, :math:`xz`, :math:`yz`)
    remain constant.
    For ``initial_box`` with volume :math:`V_0` and `final_volume` :math:`V_f`,
    ``InverseVolumeRamp`` returns arrays corresponding to boxes with volume :math:`V(t)`:

    .. math::

        V(t) &= \\begin{cases} V_0 & t < t_{\\mathrm{start}} \\\\
            \\left( \\lambda V_f^{-1} + (1 - \\lambda) V_0^{-1} \\right)^{-1} & t_{\\mathrm{start}} \\leq t < t_{\\mathrm{start}} + t_{\\mathrm{ramp}} \\\\
            V_f & t \\geq t_{\\mathrm{start}} + t_{\\mathrm{ramp}} \\end{cases}

    where :math:`\\lambda = \\frac{t - t_{\\mathrm{start}}}{t_{\\mathrm{ramp}} - t_{\\mathrm{start}}}`.

    Attributes:
        final_volume (float): The volume of the final box.
        t_start (int): The time step at the start of the ramp.
        t_ramp (int): The length of the ramp.
    """

    def __init__(self, initial_box, final_volume, t_start, t_ramp):
        BoxVariant.__init__(self)
        box = box_preprocessing(initial_box)
        _hoomd.VectorVariantBoxInverseVolumeRamp.__init__(
            self, box._cpp_obj, final_volume, t_start, t_ramp)

    @property
    def initial_box(self):
        """hoomd.Box: The initial box."""
        return Box._from_cpp(self._initial_box)

    @initial_box.setter
    def initial_box(self, box):
        box = box_preprocessing(box)
        self._initial_box = box._cpp_obj

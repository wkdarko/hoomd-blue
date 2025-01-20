// Copyright (c) 2009-2025 The Regents of the University of Michigan.
// Part of HOOMD-blue, released under the BSD 3-Clause License.

#include "AnisoPotentialPairGPU.h"
#include "EvaluatorPairALJ.h"

namespace hoomd
    {
namespace md
    {
namespace detail
    {
void export_AnisoPotentialPairALJ3DGPU(pybind11::module& m)
    {
    export_AnisoPotentialPairGPU<EvaluatorPairALJ<3>>(m, "AnisoPotentialPairALJ3DGPU");
    }
    } // end namespace detail
    } // end namespace md
    } // end namespace hoomd

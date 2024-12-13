// Copyright (c) 2009-2024 The Regents of the University of Michigan.
// Part of HOOMD-blue, released under the BSD 3-Clause License.

#ifndef MPCD_REVERSE_NONEQUILIBRIUM_SHEAR_FLOW_GPU_CUH_
#define MPCD_REVERSE_NONEQUILIBRIUM_SHEAR_FLOW_GPU_CUH_

/*!
 * \file mpcd/ReverseNonequilibriumShearFlowGPU.cuh
 * \brief Declaration of CUDA kernels for mpcd::ReverseNonequilibriumShearFlowGPU
 */

#include <cuda_runtime.h>
#ifdef __HIPCC__
#include <thrust/execution_policy.h>
#include <thrust/sort.h>
#endif // __HIPCC__

#include "hoomd/HOOMDMath.h"

namespace hoomd
    {
namespace mpcd
    {
namespace gpu
    {

//! Filter particles into slabs
cudaError_t rnes_filter_particles(Scalar2* d_particles_lo,
                                  Scalar2* d_particles_hi,
                                  unsigned int* d_num_lo_hi,
                                  const Scalar4* d_pos,
                                  const Scalar4* d_vel,
                                  const Scalar mass,
                                  const Scalar2& pos_lo,
                                  const Scalar2& pos_hi,
                                  const unsigned int num_lo_alloc,
                                  const unsigned int num_hi_alloc,
                                  const unsigned int N,
                                  const unsigned int block_size);

template<class T> void rnes_sort(Scalar2* d_particles, const unsigned int N, const T& comp);

cudaError_t rnes_copy_top_particles(Scalar2* h_top_particles,
                                    const Scalar2* d_particles,
                                    const unsigned int num_top);

cudaError_t rnes_swap_particles(Scalar4* d_vel,
                                Scalar* d_momentum_sum,
                                const Scalar2* d_particles_staged,
                                const Scalar mass,
                                const unsigned int num_staged,
                                const unsigned int block_size);

#ifdef __HIPCC__
template<class T> void rnes_sort(Scalar2* d_particles, const unsigned int N, const T& comp)
    {
    thrust::sort(thrust::device, d_particles, d_particles + N, comp);
    }
#endif

    } // end namespace gpu
    } // end namespace mpcd
    } // end namespace hoomd
#endif // MPCD_REVERSE_NONEQUILIBRIUM_SHEAR_FLOW_GPU_CUH_

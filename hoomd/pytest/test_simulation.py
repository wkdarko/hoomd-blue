import hoomd
import numpy as np
import pytest
from copy import deepcopy
import gsd.hoomd


@pytest.fixture(scope="function")
def get_snapshot(device):
    def make_snapshot(n=10, particle_types=['A']):
        s = hoomd.snapshot.Snapshot(device.comm)
        if s.exists:
            s.configuration.box = [20, 20, 20, 0, 0, 0]
            s.particles.N = n
            s.particles.position[:] = np.random.uniform(-10, 10, size=(n, 3))
            s.particles.types = particle_types
        return s
    return make_snapshot


def make_gsd_snapshot(hoomd_snapshot):
    s = gsd.hoomd.Snapshot()
    snap_properties = []
    all_attr = dir(hoomd_snapshot)
    for att in all_attr:
        if att[0] != '_' and att not in ['exists', 'replicate']:
            snap_properties.append(att)
    for prop in snap_properties:
        prop_attr = dir(getattr(hoomd_snapshot, prop))
        nested_properties = []
        for att in prop_attr:
            if att[0] != '_':
                nested_properties.append(att)
        for nested_prop in nested_properties:
            # s.prop.nested_prop = hoomd_snapshot.prop.nested_prop
            setattr(getattr(s, prop), nested_prop,
                    getattr(getattr(hoomd_snapshot, prop), nested_prop))
    return s


def update_positions(snap):
    if snap.exists:
        noise = 0.01
        rs = np.random.RandomState(0)
        mean = [0] * 3
        var = noise * noise
        cov = np.diag([var, var, var])
        shape = snap.particles.position.shape
        snap.particles.position[:] += rs.multivariate_normal(mean, cov,
                                                             size=shape[:-1])
    return snap


def assert_equivalent_snapshots(snap1, snap2):
    snap_properties = []
    all_attr = dir(snap2)
    for att in all_attr:
        if att[0] != '_' and att not in ['exists', 'replicate']:
            snap_properties.append(att)
    for prop in snap_properties:
        snap1_prop = getattr(snap1, prop)
        snap2_prop = getattr(snap2, prop)
        prop_attr = dir(snap2_prop)
        nested_properties = []
        for att in prop_attr:
            if att[0] != '_':
                nested_properties.append(att)
        for nested_prop in nested_properties:
            if nested_prop == 'types':
                assert getattr(snap1_prop, nested_prop) == \
                    getattr(snap2_prop, nested_prop)
            else:
                np.testing.assert_allclose(getattr(snap1_prop, nested_prop),
                                           getattr(snap2_prop, nested_prop))


def assert_equivalent_boxes(box1, box2):
    metadata1 = box1.get_metadata()
    metadata2 = box2.get_metadata()
    for key in metadata1:
        assert metadata1[key] == metadata2[key]


def test_initialization(device, simulation_factory, get_snapshot):
    with pytest.raises(TypeError):
        sim = hoomd.simulation.Simulation()

    sim = hoomd.simulation.Simulation(device)
    with pytest.raises(RuntimeError):
        sim.run(1)  # Before setting state

    sim = simulation_factory(get_snapshot())
    with pytest.raises(RuntimeError):
        sim.run(1)  # Before scheduling operations

    sim.operations.schedule()
    sim.run(1)


def test_run(simulation_factory, get_snapshot):
    sim = simulation_factory(get_snapshot())
    sim.operations.schedule()
    assert sim.timestep == 0
    steps = 0
    n_step_list = [1, 10, 100]
    for n_steps in n_step_list:
        steps += n_steps
        sim.run(n_steps)
        assert sim.timestep == steps
    assert sim.timestep == sum(n_step_list)


_state_args = [((10, ['A']), 10),
               ((5, ['A']), 20)]


@pytest.fixture(scope="function", params=_state_args)
def state_args(request):
    return deepcopy(request.param)


def test_state_from_gsd(simulation_factory, get_snapshot,
                        device, state_args, tmp_path):
    snap_params, nsteps = state_args

    d = tmp_path / "sub"
    d.mkdir()
    filename = d / "temporary_test_file.gsd"
    file = gsd.hoomd.open(name=filename, mode='wb+')
    sim = simulation_factory(get_snapshot(n=snap_params[0],
                                          particle_types=snap_params[1]))

    snap = sim.state.snapshot
    box = sim.state.box
    assert_equivalent_snapshots(make_gsd_snapshot(snap), snap)

    file.append(make_gsd_snapshot(snap))
    sim = hoomd.simulation.Simulation(device)
    sim.create_state_from_gsd(filename)

    assert_equivalent_boxes(box, sim.state.box)
    assert_equivalent_snapshots(snap, sim.state.snapshot)

    snapshot_dict = {}
    for step in range(1, nsteps):
        snap = update_positions(sim.state.snapshot)
        file.append(make_gsd_snapshot(snap))
        sim = hoomd.simulation.Simulation(device)
        sim.create_state_from_gsd(filename)
        assert_equivalent_boxes(box, sim.state.box)
        assert_equivalent_snapshots(snap, sim.state.snapshot)
        snapshot_dict[step] = snap

    for step, snap in snapshot_dict.items():
        sim = hoomd.simulation.Simulation(device)
        sim.create_state_from_gsd(filename, frame=step)
        assert_equivalent_boxes(box, sim.state.box)
        assert_equivalent_snapshots(snap, sim.state.snapshot)

# Copyright (c) 2009-2025 The Regents of the University of Michigan.
# Part of HOOMD-blue, released under the BSD 3-Clause License.

import hoomd
import pytest
import numpy

sqrt2inv = 1 / numpy.sqrt(2)

TOLERANCES = {"rtol": 1e-2, "atol": 1e-5}

patch_test_parameters = [
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.012090314520418179, -0.03048768233212375, -0.020302519521372915],
        0.011040513953371068,
        [
            [0.0015859062333126468, -0.0027468701721376867, -0.0015600230173152775],
            [-0.012752291970067747, 0.022087617605109952, -0.020833722138796803],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.0007999692723457226, -0.01114090834099443, -0.007274060796964416],
        0.004651059201336865,
        [
            [0.002811092008585531, 0.0004956713663675812, -0.005749113522483697],
            [-0.010690998624191522, -0.0018851115081620442, 0.008743769332283843],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.10716329368566274, -2.1122670493484197, -1.7708604149002043],
        0.19259884567130864,
        [
            [0.02766571476373035, -0.04791842359848936, -0.027214188906835586],
            [-0.22246036040275277, 0.38531264688765143, -0.3634387721364981],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.14980294587981527, -0.517897117596774, -0.6344703329732665],
        0.08113649754981586,
        [
            [0.049038756548475816, 0.008646855879890203, -0.10029176474393942],
            [-0.18650164320150397, -0.0328852716428886, 0.1525327432514915],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.2, 0.0]],
        [[-0.8, -1.3, -1.02]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.22122614255103878, -0.024932958611667055, 0.057889843743764734],
        0.08761098072205219,
        [
            [0.0, 0.0, 0.026357812134987807],
            [0.03183941405907059, -0.05514748283353311, 0.0715647331639529],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.2, 0.0]],
        [[-0.8, -1.3, -1.02]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.12732524637729745, -0.17726950238751302, 0.04481708806670525],
        0.08444761711985735,
        [
            [0.0, 0.0, -0.07724006742162585],
            [0.04854983737507447, 0.008560646238233868, -0.02682913269351473],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.2, 0.0]],
        [[-0.8, -1.3, -1.02]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-11.77816503494904, 2.165770753686239, 5.049365060463138],
        1.5283503853592224,
        [
            [0.0, 0.0, 0.4598050609835814],
            [0.5554301566509452, -0.9620332513753777, 1.2484278409832568],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyYukawa,
        {},
        {
            "pair_params": {"epsilon": 0.778, "kappa": 1.42},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.2, 0.0]],
        [[-0.8, -1.3, -1.02]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [9.652760368011261, -7.221635485842196, 3.9091112354245268],
        1.473166344037004,
        [
            [0.0, 0.0, -1.3474325459673837],
            [0.8469390714473051, 0.14933820931233416, -0.46802712346154485],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.778, "sigma": 1.19, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.0161650695094226, -0.083298288358161, -0.08000254293546676],
        0.04350539797064849,
        [
            [0.006249299816638692, -0.010824104794149086, -0.006147306411487301],
            [-0.05025069843114538, 0.08703676279856548, -0.08209575900961696],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.778, "sigma": 1.19, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.008542090040088067, -0.013333970380345037, -0.028663603086883704],
        0.01832760525404918,
        [
            [0.011077172410826152, 0.001953204365988083, -0.022654513442983346],
            [-0.04212812481497665, -0.007428325051534193, 0.034455023214604044],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.778, "sigma": 1.19, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.2662070489442997, -0.46271964969619306, -0.5323769824248823],
        0.05790134073485696,
        [
            [0.008317194070528874, -0.014405802706566608, -0.008181451032196864],
            [-0.06687866213726593, 0.1158372407639775, -0.10926125807444684],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.778, "sigma": 1.19, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.07024336682877552, -0.01273561367945491, -0.19074196840379043],
        0.024392212602781037,
        [
            [0.014742610435852588, 0.002599519985914994, -0.030150895365433757],
            [-0.05606832768380231, -0.0098863589338577, 0.04585619560409825],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 0.97},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.0027622079239978375, -0.06658185805585613, -0.056127236080865534],
        0.030522001590127953,
        [
            [0.004384309714149004, -0.007593847181023855, -0.004312754389535873],
            [-0.03525428955862503, 0.06106222070028351, -0.05759576981056035],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 0.97},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.004801569836106703, -0.016110821605886394, -0.02010947100373393],
        0.012858064120795543,
        [
            [0.007771391360802155, 0.0013703059745540929, -0.015893685096199244],
            [-0.029555750609598655, -0.005211476267562902, 0.024172546911386518],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 0.97},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.2493853854591554, -0.4584090266528183, -0.5202661071389925],
        0.05658416148091617,
        [
            [0.008127988857978328, -0.014078089665372197, -0.00799533379501422],
            [-0.06535726064326747, 0.11320209607766105, -0.10677570833468933],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyGaussian,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 0.97},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-0.06773603596583777, -0.017603283883824504, -0.18640283980247196],
        0.023837321887120035,
        [
            [0.014407235462344481, 0.0025403843294311288, -0.02946500220028324],
            [-0.05479284706295722, -0.009661457287031931, 0.04481302754015036],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyLJ,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-1.9455238094148624, -1.269674877695913, -0.12646351897802516],
        0.06877088552479703,
        [
            [0.009878541568339286, -0.017110135901044755, -0.009717316131562882],
            [-0.07943347700625308, 0.13758281799668448, -0.12977235718497987],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyLJ,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.1529938661525866, -0.9653274199711448, -0.0453098111628864],
        0.028971247285687153,
        [
            [0.017510170952057886, 0.0030875155756654327, -0.035810980321533736],
            [-0.06659376960486044, -0.011742278328420192, 0.05446456227901608],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyLJ,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-3.7101814265232987e9, -3.068632424997914e9, -8.002380847724919e8],
        8.703392435257888e7,
        [
            [1.250192189633267e7, -2.1653963916706044e7, -1.229788086412793e7],
            [-1.0052811122130676e8, 1.7411979622423828e8, -1.6423516190177378e8],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyLJ,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [2.416134421816039e8, -1.9882078394083674e9, -2.867122218281132e8],
        3.6664953859771974e7,
        [
            [2.2160233686283108e7, 3.9074470976963183e6, -4.532107051569407e7],
            [-8.427864585301311e7, -1.4860599161459792e7, 6.892836346536472e7],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedLJ,
        {},
        {
            "pair_params": {"epsilon": 0.77, "sigma": 1.13, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-33.02646286207422, -24.647019239630318, -4.818557570362859],
        2.6203325175827956,
        [
            [0.37639567238783445, -0.6519364283247793, -0.3702526039741746],
            [-3.0266023360874064, 5.242229020410042, -4.944632089877043],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedLJ,
        {},
        {
            "pair_params": {"epsilon": 0.77, "sigma": 1.13, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [2.357494589449272, -17.09094290068084, -1.7264103937244915],
        1.1038726745818228,
        [
            [0.6671787048251221, 0.11764160661479799, -1.3644825932799285],
            [-2.537379279507933, -0.4474084272678541, 2.075227947212622],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedLJ,
        {},
        {
            "pair_params": {"epsilon": 0.77, "sigma": 1.13, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-1.2494366602747592e23, -7.47190342399429e22, -2.2306585653721332e21],
        2.426065098991449e20,
        [
            [3.484902767355334e19, -6.036028652496825e19, -3.4280264595619766e19],
            [-2.8022146986448788e20, 4.853578231769241e20, -4.5780446794859164e20],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedLJ,
        {},
        {
            "pair_params": {"epsilon": 0.77, "sigma": 1.13, "delta": 0.2},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [1.0353882496245466e22, -6.044231702301891e22, -7.9920849255704e20],
        1.0220332540099799e20,
        [
            [6.177151028372888e19, 1.089198390213181e19, -1.2633219545706699e20],
            [-2.349261886272707e20, -4.142382552999396e19, 1.92137374222588e20],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyMie,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14, "n": 5.5, "m": 12.4},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-1.9185608907383984, -1.2521408460716963, -0.12476469967243964],
        0.06784706726530326,
        [
            [0.009745840396784486, -0.016880290729687938, -0.009586780745736316],
            [-0.07836642521662623, 0.13573463008274345, -0.12802908934379711],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyMie,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14, "n": 5.5, "m": 12.4},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [0.15086870266201252, -0.9519631777531574, -0.04470115198150361],
        0.02858206853600857,
        [
            [0.01727495199960542, 0.003046040127974089, -0.035329921552856386],
            [-0.06569919714356336, -0.011584541067294738, 0.0537329248027101],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyMie,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14, "n": 5.5, "m": 12.4},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-6.380949338454674e9, -5.220849829366294e9, -1.32729010034573e9],
        1.4435612149134248e8,
        [
            [2.073592532529298e7, -3.5915676205361664e7, -2.0397498990352083e7],
            [-1.6673783636332324e8, 2.887984041253813e8, -2.724035617261037e8],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyMie,
        {},
        {
            "pair_params": {"epsilon": 0.78, "sigma": 1.14, "n": 5.5, "m": 12.4},
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [4.199338440026387e8, -3.406506655464279e9, -4.755463416725215e8],
        6.081318949165459e7,
        [
            [3.675538486963374e7, 6.480966038840114e6, -7.517038913444535e7],
            [-1.3978616419268584e8, -2.464807227691403e7, 1.1432589400768268e8],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-24438.06649914493, -19392.807472482873, -4563.172146474723],
        2481.453875798641,
        [
            [356.44655547084204, -617.3835442584165, -350.6290720705163],
            [-2866.191236031939, 4964.3888450159575, -4682.564667457716],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [1654.9426299749784, -12909.362184624497, -1634.9099719140254],
        1045.366993825708,
        [
            [631.817974180563, 111.40655574459755, -1292.164485550744],
            [-2402.8971915802563, -423.69560674419665, 1965.2400595046643],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-5.545584879562406e16, -3.897295731456281e16, -6.00724551378345e15],
        6.533482491809166e14,
        [
            [9.384971254744408e13, -1.6255247040790753e14, -9.231801267129023e13],
            [-7.546467190636238e14, 1.307086459183353e15, -1.2328842607140105e15],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [4.145472181514702e15, -2.814898155635645e16, -2.152297848725213e15],
        2.7523731221791462e14,
        [
            [1.6635294786571403e14, 2.9332513029114016e13, -3.4021724623699825e14],
            [-6.326648616732528e14, -1.1155588485918328e14, 5.1743301159862644e14],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 0.0, 0.0]],
        [[0.0, 1.0, 1.0], [0.0, 0.0, 1.0], [2.0, 1.0, 0.0]],
        [[0, 0, 0], [0.9526279441628825, 0.55, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-138985.57323908593, -97123.42586287575, -21501.617361604447],
        13583.235236081233,
        [
            [0.0, 0.0, -6448.0496895867645],
            [-11825.889548882442, 20483.04154336218, -9632.374538723448],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 0.0, 0.0]],
        [[0.0, 1.0, 1.0], [0.0, 0.0, 1.0], [2.0, 1.0, 0.0]],
        [[0, 0, 0], [-0.19101299543362338, 1.0832885283134288, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [7754.7557135632205, -24687.796151765757, -3306.6477337182796],
        2063.2418829657026,
        [
            [0.0, 0.0, -4488.243718545056],
            [-3582.053557110608, -631.6126884613307, 803.2957077724617],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 0.0, 0.0]],
        [[0.0, 1.0, 1.0], [0.0, 0.0, 1.0], [2.0, 1.0, 0.0]],
        [[0, 0, 0], [0.1905255888325765, 0.11, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [-3.104239064372109e17, -2.0144530397799e17, -2.830607531087193e16],
        3.5763642622009175e15,
        [
            [0.0, 0.0, -1.6977232647401915e15],
            [-3.113668284195913e15, 5.393031666143131e15, -2.5361321851305225e15],
        ],
    ),
    (
        hoomd.md.pair.aniso.PatchyExpandedMie,
        {},
        {
            "pair_params": {
                "epsilon": 0.78,
                "sigma": 2.14,
                "n": 5.5,
                "m": 12.4,
                "delta": 0.1,
            },
            "envelope_params": {"alpha": 0.6981317007977318, "omega": 2},
        },
        [[1.0, 0.0, 0.0]],
        [[0.0, 1.0, 1.0], [0.0, 0.0, 1.0], [2.0, 1.0, 0.0]],
        [[0, 0, 0], [-0.03820259908672467, 0.21665770566268577, 0]],
        [[1.0, 0.0, 0.0, 0.0], [0.9843766433940419, 0.0, 0.0, 0.17607561994858706]],
        [1.409072519691006e16, -5.451579177557966e16, -4.353078105849488e15],
        5.4323615885809244e14,
        [
            [0.0, 0.0, -1.1817210079977378e15],
            [-9.431279149838202e14, -1.662988976709668e14, 2.115017528096385e14],
        ],
    ),
]


@pytest.fixture(scope="session")
def patchy_snapshot_factory(device):
    def make_snapshot(
        position_i=numpy.array([0, 0, 0]),
        position_j=numpy.array([2, 0, 0]),
        orientation_i=(1, 0, 0, 0),
        orientation_j=(1, 0, 0, 0),
        dimensions=3,
        L=20,
    ):
        snapshot = hoomd.Snapshot(device.communicator)
        if snapshot.communicator.rank == 0:
            N = 2
            box = [L, L, L, 0, 0, 0]
            if dimensions == 2:
                box[2] = 0
            snapshot.configuration.box = box
            snapshot.particles.N = N
            snapshot.particles.position[:] = [position_i, position_j]
            snapshot.particles.orientation[:] = [orientation_i, orientation_j]
            snapshot.particles.types = ["A", "B"]
            snapshot.particles.typeid[:] = [0, 1]
            snapshot.particles.moment_inertia[:] = [(1, 1, 1)] * N
            snapshot.particles.angmom[:] = [(0, 0, 0, 0)] * N
        return snapshot

    return make_snapshot


@pytest.mark.parametrize(
    "patch_cls, patch_args, params, patches_A, patches_B, positions,"
    "orientations, force, energy, torques",
    patch_test_parameters,
)
def test_before_attaching(
    patch_cls,
    patch_args,
    params,
    patches_A,
    patches_B,
    positions,
    orientations,
    force,
    energy,
    torques,
):
    potential = patch_cls(
        nlist=hoomd.md.nlist.Cell(buffer=0.4), default_r_cut=4, **patch_args
    )
    potential.params.default = params
    potential.directors["A"] = patches_A
    potential.directors["B"] = patches_B
    for key in params:
        assert potential.params[("A", "A")][key] == pytest.approx(params[key])
    for i, patch in enumerate(patches_A):
        # only normalized after attaching
        assert potential.directors["A"][i] == pytest.approx(patch)
    for i, patch in enumerate(patches_B):
        assert potential.directors["B"][i] == pytest.approx(patch)


@pytest.mark.parametrize(
    "patch_cls, patch_args, params, patches_A, patches_B, positions,"
    "orientations, force, energy, torques",
    patch_test_parameters,
)
def test_after_attaching(
    patchy_snapshot_factory,
    simulation_factory,
    patch_cls,
    patch_args,
    params,
    patches_A,
    patches_B,
    positions,
    orientations,
    force,
    energy,
    torques,
):
    sim = simulation_factory(patchy_snapshot_factory())
    potential = patch_cls(
        nlist=hoomd.md.nlist.Cell(buffer=0.4), default_r_cut=4, **patch_args
    )
    potential.params.default = params
    potential.directors["A"] = patches_A
    potential.directors["B"] = patches_B

    sim.operations.integrator = hoomd.md.Integrator(
        dt=0.05, forces=[potential], integrate_rotational_dof=True
    )
    sim.run(0)
    for key in params:
        assert potential.params[("A", "A")][key] == pytest.approx(params[key])
    for i, patch in enumerate(patches_A):
        # patch is returned normalized, so normalize it before checking
        nn = numpy.array(patch)
        patch = nn / numpy.linalg.norm(nn)
        assert potential.directors["A"][i] == pytest.approx(patch)
    for i, patch in enumerate(patches_B):
        # patch is returned normalized, so normalize it before checking
        nn = numpy.array(patch)
        patch = tuple(nn / numpy.linalg.norm(nn))
        assert potential.directors["B"][i] == pytest.approx(patch)


@pytest.mark.parametrize(
    "patch_cls, patch_args, params, patches_A, patches_B, positions,"
    "orientations, force, energy, torques",
    patch_test_parameters,
)
def test_forces_energies_torques(
    patchy_snapshot_factory,
    simulation_factory,
    patch_cls,
    patch_args,
    params,
    patches_A,
    patches_B,
    positions,
    orientations,
    force,
    energy,
    torques,
):
    snapshot = patchy_snapshot_factory(
        position_i=positions[0],
        position_j=positions[1],
        orientation_i=orientations[0],
        orientation_j=orientations[1],
    )
    sim = simulation_factory(snapshot)

    potential = patch_cls(
        nlist=hoomd.md.nlist.Cell(buffer=0.4), default_r_cut=4, **patch_args
    )
    potential.params.default = params
    potential.directors["A"] = patches_A
    potential.directors["B"] = patches_B

    sim.operations.integrator = hoomd.md.Integrator(
        dt=0.005, forces=[potential], integrate_rotational_dof=True
    )
    sim.run(0)

    sim_forces = potential.forces
    sim_energy = potential.energy
    sim_torques = potential.torques
    if sim.device.communicator.rank == 0:
        sim_orientations = snapshot.particles.orientation

        numpy.testing.assert_allclose(sim_orientations, orientations, **TOLERANCES)

        numpy.testing.assert_allclose(sim_energy, energy, **TOLERANCES)

        numpy.testing.assert_allclose(sim_forces[0], force, **TOLERANCES)

        numpy.testing.assert_allclose(
            sim_forces[1], [-force[0], -force[1], -force[2]], **TOLERANCES
        )

        numpy.testing.assert_allclose(sim_torques[0], torques[0], **TOLERANCES)

        numpy.testing.assert_allclose(sim_torques[1], torques[1], **TOLERANCES)

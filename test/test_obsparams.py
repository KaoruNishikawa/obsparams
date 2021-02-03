#!/usr/bin/env python3

from scripts.obsfile_params_check import obsfile_params_check as obsfile_check


def test_list_repos(token):
    check = obsfile_check(token)
    returned = check.list_repos('kaorunishikawa')
    expected = ['researches', 'obsparams', 'ros2_test', 'ros1_test']
    assert sorted(returned) == sorted(expected)


def test_list_files(token):
    check = obsfile_check(token)
    returned = check.list_files('kaorunishikawa/researches/sun_moon_scan')
    expected = [
        'sun_moon_scan/moon_scan_simulate.ipynb',
        'sun_moon_scan/sun_scan_simulate.ipynb'
    ]
    assert sorted(returned) == sorted(expected)


def test_read_file(token):
    check = obsfile_check(token)
    returned = check.read_file('kaorunishikawa/ros1_test/README.md')
    expected = '# ros1_test'
    assert returned == expected


def test_get_obsparams(token):
    check = obsfile_check(token)
    returned = check.get_obsparams('nanten2/necst-obsfiles/horizon.obs')
    expected = ['offset_Az', 'offset_El', 'lambda_on', 'beta_on', 'lambda_off', 'beta_off', 'coordsys', 'object', 'vlsr', 'tuning_vlsr', 'cosydel', 'otadel', 'start_pos_x', 'start_pos_y', 'scan_direction', 'exposure', 'otfvel', 'otflen', 'grid', 'N', 'lamdel_off', 'betdel_off', 'otadel_off', 'nTest', 'datanum', 'lamp_pixels', 'exposure_off', 'observer', 'obsmode', 'purpose', 'tsys', 'acc', 'load_interval', 'cold_flag', 'pllref_if', 'multiple', 'pllharmonic', 'pllsideband', 'pllreffreq', 'restfreq_1', 'obsfreq_1', 'molecule_1', 'transiti_1', 'lo1st_sb_1', 'if1st_freq_1', 'lo2nd_sb_1', 'lo3rd_sb_1', 'lo3rd_freq_1', 'if3rd_freq_1', 'start_ch_1', 'end_ch_1', 'restfreq_2', 'obsfreq_2', 'molecule_2', 'transiti_2', 'lo1st_sb_2', 'if1st_freq_2', 'lo2nd_sb_2', 'lo3rd_sb_2', 'lo3rd_freq_2', 'if3rd_freq_2', 'start_ch_2', 'end_ch_2', 'fpga_integtime']  # noqa: E501
    assert returned == expected

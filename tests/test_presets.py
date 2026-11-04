"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset zeigt den Effekt, den sein Hilfetext verspricht."""

import msk_constants as C
import msk_evaluation as ev
import msk_presets as P


def _view(name):
    s = ev.Settings(**C.PRESETS[name])
    return s, ev.run_view(s, C.DEFAULT_F)


def _ratio(v, rule):
    return v["runs"][rule]["value"] / v["opt"]


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name] and "Gerüst" not in C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds_and_choices():
    for preset in C.PRESETS.values():
        assert preset["inst"] in C.INSTANCES and C.V_MIN <= preset["v"] <= C.V_MAX and 0 <= preset["seed"] <= C.SEED_MAX
        assert preset["wdist"] in C.WEIGHTS and preset["cons"] in C.CONSTRAINTS and C.K_MIN <= preset["k"] <= C.K_MAX
        assert preset["okind"] in C.ORDERS and 0 <= preset["oseed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()
    d = ev.Settings()
    keys = ("inst_select", "v_slider", "seed_input", "wdist_select", "cons_select", "k_slider", "oseed_input", "okind_select")
    assert [P.SETTING_SPECS[key].default for key in keys] == [d.inst, d.v, d.seed, d.wdist, d.cons, d.k, d.oseed, d.okind]


def test_setting_specs_cover_every_preset_key_and_have_valid_defaults():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for spec in P.SETTING_SPECS.values():
        assert spec.choices is None or (spec.default in spec.choices and spec.lo in spec.choices and spec.hi in spec.choices)


def test_no_single_regler_change_of_the_default_lands_on_another_preset():
    """Das Layout setzt jeden Regler auf seinen Höchstwert (oder Tiefstwert): das darf kein Preset treffen, sonst bliebe ein Preset markiert."""
    default = dict(C.PRESETS["Standardfall (Voreinstellung)"])
    for state_key, spec in P.SETTING_SPECS.items():
        key = next(k for k, v in P.PRESET_KEYS.items() if v == state_key)
        for value in (spec.hi, spec.lo):
            if value == default[key]:
                continue
            variant = {**default, key: value}
            assert all(variant != preset for preset in C.PRESETS.values()), (state_key, value)


def test_preset_numbers_in_the_help_texts_hold():
    help_ = C.PRESET_HELP
    s, v = _view("Standardfall (Voreinstellung)")
    assert (round(_ratio(v, "wachs"), 2), round(_ratio(v, "erst"), 2), v["m"]) == (0.56, 0.21, 66) and "0,56" in help_["Standardfall (Voreinstellung)"] and "0,21" in help_["Standardfall (Voreinstellung)"]
    s, v = _view("Gutartige Gewichte")
    assert (round(_ratio(v, "erst"), 2), round(_ratio(v, "wachs"), 2), v["m"]) == (0.84, 0.55, 14) and "0,84" in help_["Gutartige Gewichte"] and "0,55" in help_["Gutartige Gewichte"]
    s, v = _view("Absteigende Reihenfolge")
    assert (_ratio(v, "erst"), _ratio(v, "fest"), _ratio(v, "wachs")) == (1.0, 0.0, 0.0) and "0,00" in help_["Absteigende Reihenfolge"] and "1,00" in help_["Absteigende Reihenfolge"]
    s, v = _view("Farben")
    assert (round(_ratio(v, "teil"), 2), round(_ratio(v, "wachs"), 2), round(_ratio(v, "erst"), 2)) == (0.64, 0.55, 0.51) and all(x in help_["Farben"] for x in ("0,64", "0,55", "0,51"))
    s, v = _view("Freie Wahl")
    assert (_ratio(v, "erst"), round(_ratio(v, "wachs"), 2), v["rank"]) == (1.0, 0.64, 14) and "0,64" in help_["Freie Wahl"] and "1,00" in help_["Freie Wahl"]


def test_presets_use_the_matroid_they_describe():
    assert ev.Settings(**C.PRESETS["Farben"]).cons == "farbe" and "teil" in ev.run_view(ev.Settings(**C.PRESETS["Farben"]))["runs"]
    assert ev.Settings(**C.PRESETS["Absteigende Reihenfolge"]).okind == "absteigend" and ev.Settings(**C.PRESETS["Gutartige Gewichte"]).inst == "plan"
    assert ev.Settings(**C.PRESETS["Freie Wahl"]).k == 14 == ev.run_view(ev.Settings(**C.PRESETS["Freie Wahl"]))["m"]

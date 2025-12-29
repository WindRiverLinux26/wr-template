addhandler deprecate_old_template_eventhandler
deprecate_old_template_eventhandler[eventmask] = "bb.event.ConfigParsed"
#
# Check possible old templates and error out.
# LAYERS_SKIP_OLD_TEMPLATE_CHECKING = "layerid1 layerid2" to skip checking for a specific layer
#
python deprecate_old_template_eventhandler () {
    files_marking_template = ["image.inc", "template.conf", "bsp-pkgs.inc", "bsp-pkgs.conf", "README"]
    bblayers = d.getVar("BBLAYERS").split()
    layers_having_templates_dir = []
    for layer in bblayers:
        templates_dir = f"{layer}/templates"
        if os.path.exists(templates_dir) and os.path.isdir(templates_dir):
            layers_having_templates_dir.append(layer)
    if not layers_having_templates_dir:
        return
    layerids_skip = (d.getVar("LAYERS_SKIP_OLD_TEMPLATE_CHECKING") or "").split()
    for layer in layers_having_templates_dir:
        layerid = bb.utils.get_file_layer(layer + '/', d)
        if layerid in layerids_skip:
            continue
        templates_dir = f"{layer}/templates"
        possible_templates = []
        for root, dirs, files in os.walk(templates_dir):
            if any(f in files for f in files_marking_template):
                possible_templates.append(root.removeprefix(f"{layer}/templates/"))
                dirs.clear()
        if possible_templates:
            msg = f"Layer {layer} contains templates in a deprecated format: {possible_templates}\n"
            msg += f"If this is deliberate, add {layerid} to LAYERS_SKIP_OLD_TEMPLATE_CHECKING.\n"
            msg += f"Otherwise, please run 'layers/wrlinux/scripts/convert-to-fragments.py {layer}' to convert the templates.\n"
            bb.fatal(msg)
}

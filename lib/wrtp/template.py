def templates_to_fragments(d):
    wr_fragments_list = []
    handled_templates = []

    # helper function to map fragment path to value
    def fragment_path_to_value(fragment_path):
        layer, subpath = fragment_path.split('conf/fragments')
        layerid = bb.utils.get_file_layer(layer, d)
        return layerid + subpath.removesuffix(".conf")

    # helper function to find fragment
    def get_fragment_path(template):
        bblayers = d.getVar("BBLAYERS").split()
        tp_bn = template.split('/')[-1]
        for layer in bblayers:
            fragment_path = "%s/conf/fragments/%s/%s.conf" % (layer, template, tp_bn)
            if os.path.exists(fragment_path) and os.path.isfile(fragment_path):
                return fragment_path
        return None

    # recursive function, extending the wr_fragments_list
    def extend_fragments_list(template, required_by=None):
        if template in handled_templates:
            return
        fragment_path = get_fragment_path(template)
        if not fragment_path:
            if required_by:
                bb.fatal('Unable to find template "%s" required by "%s"' % (template, required_by))
            else:
                bb.fatal('Unable to find template "%s"' % template)
        fragment_value = fragment_path_to_value(fragment_path)
        wr_fragments_list.append(fragment_value)
        handled_templates.append(template)
        # further parse require
        require_path = os.path.dirname(fragment_path) + "/require"
        if os.path.isfile(require_path):
            required_templates = []
            with open(require_path, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    required_templates.append(line)
            for rt in required_templates:
                extend_fragments_list(rt, required_by=template)

    # append OE_FRAGMENTS value according to WRTEMPLATE2 setting
    templates = (d.getVar("WRTEMPLATE") or "").split()
    for template in templates:
        extend_fragments_list(template)

    wr_fragments_value = " ".join(wr_fragments_list)
    return wr_fragments_value

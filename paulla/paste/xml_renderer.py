def xml_render_factory(info):
    """
    """

    def _render(value, system):
        system['request'].response_content_type = 'application/xml'
        return value

    return _render



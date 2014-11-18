<Component Guid="{{ element.guid }}" Id="{{ element.id }}">
    {% for child in element.children %}
        {% with element = child %}
            {% include child.get_template() %}
        {% endwith %}
    {% endfor %}
</Component>
<Directory Id="{{ element.id }}" Name="{{ element.name }}">
    {% for child in element.children %}
        {% with element = child %}
            {% include child.get_template() %}
        {% endwith %}
    {% endfor %}
</Directory>
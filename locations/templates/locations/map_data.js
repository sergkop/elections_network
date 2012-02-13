var electionCommissions = {};
{% for location in all_locations %}
    {% if location.x_coord %}
        electionCommissions[{{ location.id }}] = new ElectionCommission({{ location.id }}, {{ location.level }}, "{{ location.name }}",
        "{{ location.name }}", "{{ location.address }}", {{ location.x_coord|floatformat:10 }},
        {{ location.y_coord|floatformat:10 }}, {numVoters: 500, numObservers: 5});
    {% endif %}
{% endfor %}
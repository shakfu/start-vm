{% if debian_packages %}
RUN apt-get update && apt-get --no-install-recommends install -y \
{% for package in debian_packages %}
    {{package}} \
{% endfor %}
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
{% endif %}
{% if python_packages %}
 && pip install \
{% for package in python_packages %}
    {{package}} \
{% endfor %}
 && rm -rf ${HOME}/.cache /tmp/*
{% endif %}
{% if ruby_packages %}
 && gem install \
{% for package in ruby_packages %}
    {{package}} \
{% endfor %}
 && rm -rf /tmp/*
{% endif %}

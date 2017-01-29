RUN echo "STARTING" \
{% for section in sections %}
 ##
 ## section: {{section.name}}
 ##
{% if section.pre_install %}
{{section.pre_install | junction}}
{% endif %}
{% if section.type == "debian_packages" %}
 && apt-get update && apt-get --no-install-recommends install -y \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
{% endif %}

{% if section.type == "python_packages" %}
 && pip3 install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && rm -rf ${HOME}/.cache /tmp/*
{% endif %}

{% if section.type == "ruby_packages" %}
 && gem install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && rm -rf ${HOME}/.cache /tmp/*
{% endif %}

{% if section.type == "rlang_packages" %}
 && Rscript -e "install.packages({{rlang_packages | sequence}})"
 && rm -rf ${HOME}/.cache /tmp/*
{% endif %}

{% if section.purge %}
 && apt-get purge -y \
{% for package in section.purge %}
    {{package}} \
{% endfor %}
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
{% endif %}

{% if section.post_install %}
{{section.post_install | junction}}
{% endif %}

{% endfor %}

%define _build_id_links none

Name:        {{ package }}
Version:     {{ version }}
Summary:     {{ summary }}
BuildRoot:   {{ buildroot }}
Vendor:      {{ company }}
URL:         {{ url }}
Group:       Utilities
License:     Commercial
AutoReqProv: no
Release:     1

{{ dependencies }}

%description
{{ description }}

%files
%defattr(-,root,root)
{% for directory in directories %}
{{ ['%dir', directory] | join(' ') }}
{% endfor %}
{% for file in files %}
{{ file }}
{% endfor %}

%pre
{% include 'preinstall' %}

%posttrans
{% include 'postinstall' %}

%preun
{% include 'preremove' %}

%postun
{% include 'postremove' %}

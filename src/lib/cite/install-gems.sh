#!/bin/zsh

set -e

here="$( cd "$( dirname "$0" )"; pwd )"

gem install -N -f -i "$here" -v '1.0.0' 'namae'
gem install -N -f -i "$here" -v '1.4.5' 'csl'
gem install -N -f -i "$here" -v '1.0.7' 'citeproc'
gem install -N -f -i "$here" -v '1.1.8' 'citeproc-ruby'
gem install -N -f -i "$here" -v '1.4.0' 'unicode_utils'

command rm -rf "${here}/gems/namae-0.*"
command rm -rf "${here}/doc" "${here}/build_info" "${here}/cache" "${here}/specifications" "${here}/"*.gem

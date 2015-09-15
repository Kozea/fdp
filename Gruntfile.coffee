module.exports = (grunt) ->
  coffees = 'coffees/**/*.coffee'
  coffee_deps = "bower_components/**/*.coffee"

  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')

    uglify:
      options:
        banner: '/*! <%= pkg.name %>
          <%= grunt.template.today("yyyy-mm-dd") %> */\n'

      fdp:
        files:
          'fdp/static/js/fdp.min.js': ['fdp/static/js/fdp.js']
      deps:
        files:
          'fdp/static/js/deps.min.js': ['fdp/static/js/deps.js']

    coffee:
      fdp:
        options:
          bare: true
          join: true
          sourceMap: true

        files:
          'fdp/static/js/fdp.js': coffees

      deps:
        options:
          bare: true
          join: true
          sourceMap: true

        files:
          'fdp/static/js/deps.js': coffee_deps

    coffeelint:
      options:
        no_backticks:
          level: 'ignore'

      fdp: coffees

    watch:
      options:
        livereload: true

      coffee:
        files: ['Gruntfile.coffee'].concat(coffees)
        tasks: ['coffeelint', 'coffee']

  grunt.loadNpmTasks 'grunt-coffeelint'
  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  grunt.registerTask 'default', ['coffeelint', 'coffee', 'uglify']
  grunt.registerTask 'js', ['coffeelint', 'coffee', 'uglify']
  grunt.registerTask 'dev', ['coffeelint', 'coffee', 'uglify', 'watch']

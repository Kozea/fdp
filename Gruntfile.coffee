module.exports = (grunt) ->
  coffees = 'coffees/**/*.coffee'

  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')

    uglify:
      options:
        banner: '/*! <%= pkg.name %>
          <%= grunt.template.today("yyyy-mm-dd") %> */\n'

      fdp:
        files:
          'fdp/static/js/fdp.min.js': ['fdp/static/js/fdp.js']

    coffee:
      fdp:
        options:
          bare: true
          join: true
          sourceMap: true

        files:
          'fdp/static/js/fdp.js': coffees

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

  grunt.registerTask 'default', ['coffeelint', 'coffee', 'uglify:fdp']
  grunt.registerTask 'js', ['coffeelint', 'coffee', 'uglify:fdp']
  grunt.registerTask 'dev', ['coffeelint', 'coffee', 'uglify:fdp', 'watch']

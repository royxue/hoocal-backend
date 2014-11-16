'use strict';

var
  // https://www.npmjs.org/package/gulp
  gulp = require('gulp'),
  // https://www.npmjs.org/package/gulp-autoprefixer
  prefix = require('gulp-autoprefixer'),
  // https://www.npmjs.org/package/gulp-clean
  clean = require('gulp-clean'),
  // https://www.npmjs.org/package/gulp-coffee
  coffee = require('gulp-coffee'),
  // https://www.npmjs.org/package/gulp-concat
  concat = require('gulp-concat'),
  // https://www.npmjs.org/package/gulp-connect
  connect = require('gulp-connect'),
  // https://www.npmjs.org/package/gulp-filter
  gulpFilter = require('gulp-filter'),
  // https://www.npmjs.org/package/gulp-header
  header = require('gulp-header'),
  // https://www.npmjs.org/package/gulp-inject
  inject = require('gulp-inject'),
  // https://www.npmjs.org/package/gulp-jade
  jade = require('gulp-jade'),
  // https://www.npmjs.org/package/gulp-less
  less = require('gulp-less'),
  // https://www.npmjs.org/package/main-bower-files
  bowerFiles = require('main-bower-files'),
  // https://www.npmjs.org/package/gulp-minify-css
  minifyCSS = require('gulp-minify-css'),
  // https://www.npmjs.org/package/gulp-ngmin
  ngmin = require('gulp-ngmin'),
  // https://www.npmjs.org/package/gulp-rev
  rev = require('gulp-rev'),
  // https://www.npmjs.org/package/gulp-sourcemaps
  sourcemaps = require('gulp-sourcemaps'),
  // https://www.npmjs.org/package/gulp-uglify
  uglify = require('gulp-uglify'),
  // https://www.npmjs.org/package/gulp-util
  gutil = require('gulp-util'),
  browserSync = require('browser-sync'),
  jshint = require('gulp-jshint'),
  stylish = require('jshint-stylish');

// Default development environment configured
// Set to production by run task "prod"
var env = 'development';
// And this var can be setted by process.env.NODE_ENV
// var env = process.env.NODE_ENV;

gulp.task('env:prod', function () {
  env = 'production';
});
gulp.task('env:dev', function () {
  env = 'development';
});

// The banner will insert in scripts and styles
var banner = '/* (c) 2014 Edward. */\n';

// The current path configuration
var path_current = false;

gulp.task('check', function () {
  if (! path_current) {
    gutil.log(gutil.colors.red('Error: path not setted. Please have a look at usage below:'));
    gulp.start('default');
    throw new Error('Path not setted')
  }
});

// All path and path switch tasks defined below:
var paths = {
  hoocal : {
    name: 'HooCal',
    src_path_views: ['src/hoocal/views/**/*.jade'],
    src_path_scripts: ['src/hoocal/scripts/**/*.coffee', 'src/hoocal/scripts/**/*.js', 'src/common/scripts/**/*.coffee'],
    src_path_styles: ['src/hoocal/styles/**/*.less', 'src/hoocal/styles/**/*.css', 'bower_components/angular-material/themes/**/*.css'],
    src_path_images: ['src/hoocal/images/**/*.jpg', 'src/hoocal/images/**/*.svg', 'src/hoocal/images/**/*.png'],
    dest_path: 'dev/hoocal/',
    bower_config: 'src/hoocal/bower.json',
    // Two custom vars
    dest_path_prod: 'prod/hoocal/',
    dest_path_dev: 'dev/hoocal/'
  }
};

gulp.task('path:hoocal', function () {
  if (env === 'production') {
    paths.hoocal.dest_path = paths.hoocal.dest_path_prod;
  }
  path_current = paths.hoocal;
  gutil.log('Switch to path: ' + path_current.name);
});

// Display information
gulp.task('info', ['check'], function () {
  gutil.log('==    Env     ==');
  gutil.log('Environment    :' + env);
  gutil.log('==    Path    ==');
  gutil.log('Path           :' + path_current.name);
  gutil.log('Source views   :' + path_current.src_path_views);
  gutil.log('Source scripts :' + path_current.src_path_scripts);
  gutil.log('Source styles  :' + path_current.src_path_styles);
  gutil.log('Source images  :' + path_current.src_path_images);
  gutil.log('Dest           :' + path_current.dest_path);
  gutil.log('Bower config   :' + path_current.bower_config);
});


// Clean the outputs
gulp.task('clean', ['check'], function () {
  gulp.src(
      // Dest dir
      [path_current.dest_path,
      // Git dir excepted
      '!' + path_current.dest_path + '.git/'],
      {read: false})
    .pipe(clean());
});

// Styles pipe, includes less complie, concat and filerev
gulp.task('pipe:styles', ['check'], function () {
  var less_filter = gulpFilter('**/*.less');
  var css_filter = gulpFilter('**/*.css');
  var files
    = bowerFiles({
        paths: {
          bowerJson: path_current.bower_config
        }
      });
  files = files.concat(path_current.src_path_styles);
  gulp.src(files)
    .pipe(less_filter)
    .pipe(less())
    .pipe(less_filter.restore())
    .pipe(css_filter)
    .pipe(prefix())
    .pipe(env === 'production' ? concat('min.css') : gutil.noop() )
    .pipe(env === 'production' ? minifyCSS() : gutil.noop() )
    .pipe(env === 'production' ? header(banner) : gutil.noop() )
    .pipe(env === 'production' ? rev() : gutil.noop() )
    .pipe(gulp.dest(path_current.dest_path + 'static/'))
    .pipe(browserSync.reload({stream:true}));
});

// Scripts pipe, includes coffee complie, bower compments dependencies, concat, source maps and filerev
gulp.task('pipe:scripts', ['check'], function () {
  var coffee_filter = gulpFilter('**/*.coffee');
  var js_filter = gulpFilter('**/*.js');
  var files
    = bowerFiles({
        paths: {
          bowerJson: path_current.bower_config
        }
      });
  files = files.concat(path_current.src_path_scripts);
  gulp.src(files)
    .pipe(env === 'development' ? sourcemaps.init() : gutil.noop())
    .pipe(coffee_filter)
    .pipe(coffee())
    .pipe(coffee_filter.restore())
    .pipe(js_filter)
    .pipe(env === 'production' ? ngmin() : gutil.noop())
    .pipe(concat('min.js'))
    .pipe(env === 'production' ? uglify() : gutil.noop())
    .pipe(env === 'development' ? sourcemaps.write() : gutil.noop())
    .pipe(env === 'production' ? header(banner) : gutil.noop())
    .pipe(env === 'production' ? rev() : gutil.noop())
    .pipe(gulp.dest(path_current.dest_path + 'static/'))
    .pipe(browserSync.reload({stream:true}));
});

gulp.task('pipe:images', ['check'], function () {
  gulp.src(path_current.src_path_images)
    .pipe(gulp.dest(path_current.dest_path + 'images/'))
    .pipe(browserSync.reload({stream:true}));
});

// Views pipe, includes jade complie and include the static scripts
gulp.task('pipe:views', ['check'], function () {
  var jade_filter = gulpFilter('**/*.jade');
  gulp.src(path_current.src_path_views)
    .pipe(jade_filter)
    .pipe(jade())
    .pipe(jade_filter.restore())
    .pipe(inject(gulp.src(['**/*.css', '**/*.js'], {read: false, cwd: path_current.dest_path}), {addRootSlash: true}))
    .pipe(gulp.dest(path_current.dest_path))
    .pipe(browserSync.reload({stream:true}));
});

gulp.task('connect', ['check'], function() {
  connect.server({
    root: path_current.dest_path,
    livereload: true,
  });
});

gulp.task('browser-sync', ['check'], function() {
    browserSync({
        server: {
            baseDir: path_current.dest_path
        },
        browser: false,
        ghostMode: false
    });
});


gulp.task('watch', ['browser-sync'], function() {
  gulp.watch(path_current.src_path_scripts, ['pipe:scripts']);
  gulp.watch(path_current.src_path_styles, ['pipe:styles']);
  gulp.watch(path_current.src_path_views, ['pipe:views']);
  gulp.watch(path_current.src_path_images, ['pipe:images']);
});

// There's a bug in gulp-insert, so whole pipe splited to two part: pipe:res and pipe:views
gulp.task('pipe:res', ['pipe:styles', 'pipe:scripts', 'pipe:images']);
gulp.task('pipe:all', ['pipe:styles', 'pipe:scripts', 'pipe:images', 'pipe:views']);
gulp.task('hoocal:prod', ['env:prod', 'path:hoocal', 'clean', 'pipe:all']);
gulp.task('hoocal:prod:clean', ['env:prod', 'path:hoocal', 'clean']);
gulp.task('hoocal:prod:watch', ['env:dev', 'path:hoocal', 'watch']);
gulp.task('hoocal:dev', ['env:dev', 'path:hoocal', 'pipe:all']);
gulp.task('hoocal:dev:clean', ['env:dev', 'path:hoocal', 'clean']);
gulp.task('hoocal:dev:watch', ['env:dev', 'path:hoocal', 'watch']);


// Help information
gulp.task('default', function () {
  gutil.log('\n\n== Edward\'s FE build tool ==\n\nUsage : gulp [env:environment] path:path_name task [task2 task3 ..]\nSample: gulp env:prod path:hoocal watch\n== ==');
});

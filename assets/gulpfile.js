/* requires */
var gulp = require('gulp'),
// fileinclude = require('gulp-file-include'),
// template = require('gulp-template'),
// webserver = require('gulp-webserver'),
// RevAll = require('gulp-rev-all'),
uglify = require('gulp-uglify'),
// filter = require('gulp-filter'),
// csso = require('gulp-csso'),
// minifyCss = require('gulp-minify-css'),
// gulpif = require('gulp-if'),
rename = require('gulp-rename'),
// livereload = require('gulp-livereload'),
// minifyHtml = require("gulp-minify-html"),
// useref = require('gulp-useref'),
// less = require('gulp-less'),
sass = require('gulp-sass');


/* tasks */
gulp.task('server', function() {
	gulp.src('src').pipe(webserver({
        port: '8080',
  		fallback: 'index.html'
	}));
});

gulp.task('minHTML', function() {
    gulp.src('src/index.html') // 要压缩的html文件
    .pipe(minifyHtml()) //压缩
    .pipe(gulp.dest('dist'))
    .pipe(livereload());
});

gulp.task('minify-css', function () {
    gulp.src('src/css/*.css') // 要压缩的css文件
    .pipe(minifyCss()) //压缩css
    .pipe(rename({suffix: '.min'}))
    .pipe(gulp.dest('dist/css'));
});

gulp.task('minify-js', function () {
    gulp.src('js/*.js') // 要压缩的js文件
    .pipe(uglify())  //使用uglify进行压缩,更多配置请参考：
    .pipe(rename({suffix: '.min'}))
    .pipe(gulp.dest('dist/js')); //压缩后的路径
});

gulp.task('compile-less', function () {
    gulp.src('less/*.less')
    .pipe(less())
    .pipe(gulp.dest('dist/css'));
});

gulp.task('compile-sass', function () {
    gulp.src('scss/*.scss')
    .pipe(sass())
    .pipe(gulp.dest('dist/css'));
});

// 自动刷新
gulp.task('less', function() {
  gulp.src('less/*.less')
    .pipe(less())
    .pipe(gulp.dest('css'))
    .pipe(livereload());
});

gulp.task('watch', function() {

  livereload.listen(); //要在这里调用listen()方法
  gulp.watch('src/js/*.js', ['minify-js']);
  gulp.watch('src/css/*.css', ['minify-css']);
  gulp.watch('src/index.html', ['minHTML']);
});

gulp.task('default', function() {
    gulp.start('compile-sass');
    gulp.start('minify-js');
});
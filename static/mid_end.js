var app = angular.module('myApp', []);
app.config(function($interpolateProvider) { 
	$interpolateProvider.startSymbol('(('); 
	$interpolateProvider.endSymbol('))');
});

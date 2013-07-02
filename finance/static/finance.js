var financeServices = angular.module('financeServices', ['ngResource']);
financeServices.factory('Snapshot', function($resource) {
    return $resource('/api/v1/snapshots', {}, {
    });
});
financeServices.factory('Stock', function($resource) {
    return $resource('/api/v1/stocks/:snapshot', {}, {
    });
});
var financeFilters = angular.module('financeFilters', []);

var financeApp = angular.module('financeApp', ['financeServices', 'financeFilters'], function($routeProvider) {
    $routeProvider.
    when('/', {controller:Snapshots, templateUrl:'/static/snapshots.html'}).
    when('/stocks/:snapshot', {controller:Stocks, templateUrl:'/static/stocks.html'}).
    otherwise({redirectTo:'/'});
});

function Snapshots($scope, Snapshot) {
    $scope.snapshots = Snapshot.query();
}

function Stocks($scope, Stock, $routeParams) {
    $scope.stocks = Stock.query({snapshot: $routeParams.snapshot});
}

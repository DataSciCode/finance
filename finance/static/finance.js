var financeServices = angular.module('financeServices', ['ngResource']);
financeServices.factory('Snapshot', function($resource) {
    return $resource('/api/v1/snapshots', {}, {
    });
});
financeServices.factory('Stock', function($resource) {
    return $resource('/api/v1/snapshots/:snapshot/stocks/:stock', {}, {
    });
});
var financeFilters = angular.module('financeFilters', []);

var financeApp = angular.module('financeApp', ['financeServices', 'financeFilters'], function($routeProvider) {
    $routeProvider.
    when('/', {controller:Snapshots, templateUrl:'/static/home.html'}).
    when('/snapshots/:snapshot/stocks', {controller:Stocks, templateUrl:'/static/stocks.html'}).
    when('/snapshots/:snapshot/stocks/:stock', {controller:Stock, templateUrl:'/static/stock.html'}).
    otherwise({redirectTo:'/'});
});

function Snapshots($scope, Snapshot) {
    $scope.snapshots = Snapshot.query();
}

function Stocks($scope, Stock, $routeParams, $location) {
    $scope.stocks = Stock.query({snapshot: $routeParams.snapshot});

    $scope.search = function() {
        $location.path("/snapshots/"+$routeParams.snapshot+"/stocks/"+$scope.stockTicker);
    }
}

function Stock($scope, Stock, $routeParams) {
    $scope.stock = Stock.get({snapshot: $routeParams.snapshot, stock: $routeParams.stock});
}

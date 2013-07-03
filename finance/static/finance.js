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

function loadDisqus(currentPageId) {
	console.log(currentPageId);
	if (typeof DISQUS === 'undefined') {
		console.log("loading");
		window.disqus_shortname = 'nicksfinance';
		window.disqus_identifier = currentPageId; 
		window.disqus_url = "http://finance.nmr.io/#!"+currentPageId; 
		var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
		dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
		(document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
	} else {
		console.log("resetting");
		DISQUS.reset({
			reload: true,
			config: function() {
				this.page.identifier = currentPageId,
				this.page.url = "http://finance.nmr.io/#!"+currentPageId
			}
		});
	}
}

var financeApp = angular.module('financeApp', ['financeServices', 'financeFilters'], function($routeProvider) {
    $routeProvider.
    when('/', {controller:Snapshots, templateUrl:'/static/home.html'}).
    when('/snapshots/:snapshot/stocks', {controller:Stocks, templateUrl:'/static/stocks.html'}).
    when('/snapshots/:snapshot/stocks/:stock', {controller:Stock, templateUrl:'/static/stock.html'}).
    otherwise({redirectTo:'/'});
});

var routeChanged = function($location) {
	return function(event, next, current) { 
		loadDisqus($location.path());
	}
};

function Snapshots($scope, Snapshot, $location) {
	$scope.$on('$routeChangeSuccess', routeChanged($location));
    $scope.snapshots = Snapshot.query();
}

function Stocks($scope, Stock, $routeParams, $location) {
	$scope.$on('$routeChangeSuccess', routeChanged($location));
    $scope.stocks = Stock.query({snapshot: $routeParams.snapshot});

    $scope.search = function() {
        $location.path("/snapshots/"+$routeParams.snapshot+"/stocks/"+$scope.stockTicker);
    }
}

function Stock($scope, Stock, $routeParams, $location) {
	$scope.$on('$routeChangeSuccess', routeChanged($location));
    $scope.stock = Stock.get({snapshot: $routeParams.snapshot, stock: $routeParams.stock});
}

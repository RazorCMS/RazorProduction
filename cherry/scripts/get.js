function mainCtrl($scope, $http, $location, $window){
    $scope.tasks = {};
    $scope.headers = [];
    $scope.label = "";
    $scope.version = 1;
    $scope.status = null;
    //$scope.label_version = [$scope.label,$scope.version];
    $scope.label_version = $scope.label+" "+$scope.version;

    //console.log( $location );
    //    console.log( $location.absUrl() );

    //    console.log( $location.path("/") );
    //    console.log( $location.path() );
    //    console.log( $location.search() );
    //    console.log( $location.hash() );

    // var promise = $http.get("/db/tasks/_all_docs");
    // not possible because of CORS

    $scope.fetch = function( l, v){
	if (l == ""){
	    console.log('empty campaign');
	    return
	}
	$scope.label = l;
	$scope.version = v;
	url = 'db/tasks/_design/tasks/_view/label-version?include_docs=true&key=["'+l+'",'+v+']';
	console.log('getting it '+l+" "+v);
	$http({method:'GET', url: url}).success(function(data,status){
		$scope.tasks = _.pluck(data.rows,'doc');
		console.log( $scope.tasks);
		    //filter by version and label
		    // $scope.tasks = _.filter( $scope.tasks, function(item) { return (item.version == $scope.version && item.label == $scope.label);})
		    if ($scope.status){
			$scope.tasks = _.filter( $scope.tasks, function(item) { return (item.status == $scope.status);})
			    }
		    
		    if ( $scope.tasks.length !=0 ){
			// in one go
			//$scope.headers = _.filter(_.keys($scope.tasks[0]), function(item) { return item.indexOf("_")!=0;})
			//if ($scope.headers.indexOf( 'taskinfo') == -1){
			//    $scope.headers.push('taskinfo');
			//}
			_.each( $scope.tasks, function(task_item){

				var new_headers = _.filter(_.keys(task_item), function(key_item) { return key_item.indexOf("_")!=0;});
				
				_.each( new_headers, function( key_item) { 
					if ($scope.headers.indexOf( key_item ) == -1){
					    $scope.headers.push( key_item );
					}
				    });
			    });
			if ($scope.headers.indexOf( '_id') == -1){
			    $scope.headers.push('_id');
			}
		    }
		    //console.log( $scope.headers ) ;		    
		    //		    console.log( $scope.tasks );
	    }).error( function(status){
			console.log("fail data");
		    });
    };
    $scope.$watch("label_version", function(elem){ //watch nEvents -> is user leaves empty remove nEvents, as not to save null
	    //console.log('watching', elem);
	    //console.log('watching', typeof elem );
	    elems = elem.split(" ");
	    console.log( elems )
	    $scope.fetch( elems[0], elems[1]);
	});

    
    $http({method :'GET', url:'rest/getmain'}).success(function(data,status){
	    //console.log(data);
	    if ($location.search()["label"] === undefined){
		$scope.label = data.rows[0].doc.label;
	    }else{
		$scope.label = $location.search()["label"];
	    }
	    
	    if ($location.search()["version"] === undefined){
		$scope.version = data.rows[0].doc.version;
	    }else{
		$scope.version = $location.search()["version"];
	    }
	    if ($location.search()["status"] === undefined){
		$scope.status = null;
	    }else{
		$scope.status = $location.search()["status"];
	    }
	    $http({method:'GET', url: 'db/prods/_design/prods/_view/label-version'}).success(function(data,status){
		    $scope.prods = _.pluck(data.rows,'key');
		    console.log("prod",$scope.prods);
		    console.log(typeof $scope.prods);
		}).error( function(status){
			consolde.lo("wath-tatus");
			console.log("fail data");
		    });
	    //	    $http({method:'GET', url: 'rest/getdocs?label='+$scope.label+'&version='+$scope.version}).success(function(data,status){
	    // bypass the rest api 

	    // get some data
	    $scope.fetch( $scope.label, $scope.version);


	}).error( function(status){
		console.log("fail main");
	    });

}
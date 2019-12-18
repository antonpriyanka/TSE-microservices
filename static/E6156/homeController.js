

/*
    This is the way that old, obsolete guys build services and controllers.
 */
CustomerApp.controller("homeController", function($scope, $http, $location, $window, CustomerService) {

    console.log("Loaded.")

    $scope.register = false;
    $scope.loginRegisterResult = false;
    $scope.useEmailLogin = false;
    $scope.menuSelection = 'home';

    $scope.lemail = null;
    $scope.password = null;
    $scope.password2 = null;
    $scope.lastName = null;
    $scope.firstName = null;

    $scope.customerInfo = null;

    console.log("Controller loaded.");
    console.log("Base URL = " + $location.absUrl());
    console.log("Host = " + $location.host());
    console.log("Port = " + $location.port());
    console.log("Protocol = " + $location.protocol());

    baseUrl = "http://127.0.0.1:5000/api";
    // baseUrl = "http://tse6156.xbpsufqtgm.us-east-1.elasticbeanstalk.com/api";
    var customer_service_base_url = "https://rpdp3zsx2m.execute-api.us-east-1.amazonaws.com/live/api";


    console.log("CustomerService version = " + CustomerService.get_version());

    // This should be a separately injected service.
    // I am lazy and for got how to do this.
    sStorage = $window.sessionStorage;

    $scope.navMenu = function(selection) {
        console.log("Selection = " + selection);
        $scope.menuSelection = selection;
    };

    $scope.getNavClass = function(selection) {
        if (selection == $scope.menuSelection) {
            return "nav-item active";
        }
        else {
            return "nav-item";
        }
    };

    $scope.doLogin = function() {
        console.log("doing login")
        $("#loginModal").modal();
    };

    $scope.doLogout = function() {
        console.log('doing logout');
        // implement logout
    }

    $scope.checkLoginOnLoad = function() {
        console.log("Checking login on page load")

        // if session storage auth token is undefined, return
        // else call an API to get the original email for it

        CustomerService.checkLogin($scope).then(function (result) {
            console.log("Resolved!")
            $scope.loginRegisterResult = true;
            console.log($scope.lemail);
            CustomerService.getCustomer($scope.lemail)
                .then(function(c) {
                    console.log("checking customerInfo respo");
                    console.log(c);
                    $scope.customerInfo = c;
                    $scope.$apply();
                })
                .catch(function(error) {
                    console.log("Boom!")
                });
        }).
            catch(function(error) {
            console.log("Error");
            console.log(error);
        })        
    };

    $scope.driveLogin = function() {
        if(!$scope.register) { // for login
            CustomerService.driveLogin(
                $scope.lemail, $scope.password
            ).then(function (result) {
                console.log("Resolved!")
                $scope.loginRegisterResult = true;
                CustomerService.getCustomer($scope.lemail)
                    .then(function(c) {
                        console.log("checking customerInfo respo");
                        console.log(c);
                        $scope.customerInfo = c;
                        $scope.$apply();
                    })
                    .catch(function(error) {
                        console.log("Boom!")
                    });
            }).
                catch(function(error) {
                console.log("Error");
            })
        }
        else { // for register
            CustomerService.driveRegister(
                $scope.lemail, $scope.password, $scope.password2, $scope.firstName, $scope.lastName
            ).then(function (result) {
                console.log("Resolved!")
                $scope.loginRegisterResult = true;
                CustomerService.getCustomer($scope.lemail)
                    .then(function(c) {
                        $scope.customerInfo = c;
                        $scope.$apply();
                    })
                    .catch(function(error) {
                        console.log("Boom!")
                    });
            }).
                catch(function(error) {
                console.log("Error");
            })
        }
    };



    $scope.loginOK = function() {
        if (!$scope.register) {
            if (($scope.lemail && $scope.password) &&
                ($scope.lemail.length > 0) &&
                ($scope.password.length > 0)) {
                return true;
            }
            else {
                return false;
            }
        }
        else {
            if (($scope.lemail && $scope.password && $scope.password2) &&
                ($scope.lastName && $scope.firstName) &&
                ($scope.lemail.length > 0) &&
                ($scope.password.length > 0) &&
                ($scope.password2.length > 0) &&
                ($scope.lastName.length > 0) &&
                ($scope.firstName.length > 0)) {
                return true;
            }
            else {
                return false;
            }

        }
    };


    var urlBase = "http://127.0.0.1:5000"
    // var urlBase = "http://tse6156.xbpsufqtgm.us-east-1.elasticbeanstalk.com"
    var urlBase = "https://rpdp3zsx2m.execute-api.us-east-1.amazonaws.com/live/api";





});


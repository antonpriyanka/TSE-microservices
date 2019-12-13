(function() {
    'use strict';
    /*
    @CommentService
    */
    angular
        .module('CustomerApp')

    .factory('CustomerService', [
        '$http', '$window',
        function($http, $window) {

            console.log("Hello!")

            var version = "678";

            // This is also not a good way to do this anymore.
            var sStorage = $window.sessionStorage;

            var customer_service_base_url = "http://127.0.0.1:5000/api"
            // var customer_service_base_url = "http://tse6156.xbpsufqtgm.us-east-1.elasticbeanstalk.com/api"

            return {
                get_version: function () {
                    return ("1234");
                },
                driveLogin: function (email, pw) {

                    return new Promise(function(resolve, reject) {
                        console.log("Driving login.")
                        var url = customer_service_base_url + "/login";
                        console.log("email = " + email);
                        console.log("PW = " + pw);

                        var bd = {"email": email, "password": pw};

                        $http.post(url, bd).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))

                                var auth = h.authorization;
                                sStorage.setItem("token", auth);
                                resolve("OK")
                                $('#loginModal').modal('hide');
                            }).error(function (error) {
                                var error_msg = JSON.stringify(error);
                                console.log("Error = " + error_msg);
                                // $('#ErrorMessageLogin').innerHTML = "ERROR";
                                // $scope.ErrorMessageLoginText = 'test'
                                alert(error_msg);
                                reject("Error")
                            });
                    });
                },
                checkLogin: function ($scope) {

                    return new Promise(function(resolve, reject) {
                        console.log("Check login.")
                        var url = customer_service_base_url + "/user";
                        
                        let headers1 = {
                            'Content-Type': 'application/json',
                            'authorization': sStorage.getItem("token") };
                        let options = { headers: headers1 };

                        $http.post(url, null, options).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data;
                                console.log(result);
                                $scope.lemail = result.email;
                                // console.log(result.email);
                                // console.log($scope.lemail);
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))

                                // var auth = h.authorization;
                                // sStorage.setItem("token", auth);
                                resolve("OK")
                            }).error(function (error) {
                                console.log("Error = " + JSON.stringify(error, null, 4));
                                reject("Error")
                            });
                    });
                },
                driveRegister: function (email, pw, pw2, fname, lname) {

                    // what about pw2??
                    return new Promise(function(resolve, reject) {
                        console.log("Driving Register");
                        var url = customer_service_base_url + "/registrations";
                        console.log("email = " + email);
                        console.log("PW = " + pw);
                        console.log("PW2 = " + pw2);
                        console.log("first name = " + fname);
                        console.log("last name = " + lname);

                        var bd = {"email": email, 
                                 "password": pw,
                                 "first_name": fname,
                                 "last_name": lname};

                        $http.post(url, bd).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))

                                var auth = h.authorization;
                                sStorage.setItem("token", auth);
                                resolve("OK")
                            }).error(function (error) {
                                console.log("Error = " + JSON.stringify(error, null, 4));
                                reject("Error")
                            });
                    });
                },

                getCustomer: function (email) {
                    return new Promise(function(resolve, reject) {
                        var url = customer_service_base_url + "/user/" + email;

                        $http.get(url).success(
                            function (data, status, headers) {
                                var rsp = data;
                                console.log("RSP = " + JSON.stringify(rsp, null, 4));
                                resolve(rsp)
                            }).error(function (error) {
                                console.log("Error = " + JSON.stringify(error, null, 4));
                                reject("Error")
                            });
                    });
                }
            }
        }
    ])
})();
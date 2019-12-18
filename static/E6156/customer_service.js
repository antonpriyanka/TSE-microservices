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

//once window is loaded, get the URL
            console.log('hello!');
            console.log(window.location.hash);
            var id_token = getHashParams('id_token'); //this contains the encoded JWT token from facebook, sending to backend
            var access_token = getHashParams('access_token');
            var expiration = getHashParams('expires_in');
            console.log("id_token");
            console.log(id_token);
            if(id_token && id_token.length > 0){
                //To do: Validate the authenticity of the JWT token
                var id_token_obj = parseJwt(id_token)
                console.log('userID='+id_token_obj['cognito:username'].toString())
                console.log('email='+id_token_obj['email'].toString()) //get email from the ID token
                console.log('email='+id_token_obj['given_name'].toString()) //get the given name from the ID token
                console.log('access_token='+access_token.toString())
                console.log("Done setting everything");
            }

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
                        
                        var headers1;
                        if(id_token && id_token.length > 0)
                        {
                            headers1 = {
                                'Content-Type': 'application/json',
                                'authorization': id_token };       
                        }
                        else{
                            headers1 = {
                                'Content-Type': 'application/json',
                                'authorization': sStorage.getItem("token") };
                        }
                        let options = { headers: headers1 };

                        $http.post(url, null, options).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data;
                                console.log(result);
                                $scope.lemail = result.email;
                                $scope.loginRegisterResult = true;
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
                },

                doUpdatePersonal: function ($scope, data) {
                    console.log(data);
                    var email = $scope.lemail;
                    return new Promise(function(resolve, reject) {
                        console.log("Updating personal details.")
                        var url = customer_service_base_url + "/user/" + email;
                        console.log("email = " + email);
                        console.log("data = " + data);
                        // console.log("PW = " + pw);

                        let headers1 = {
                            'Content-Type': 'application/json',
                            'authorization': sStorage.getItem("token"),
                            'Etag': sStorage.getItem("personal_etag") };
                        let options = { headers: headers1 };

                        var bd = data;

                        $http.put(url, bd, options).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))
                                resolve("OK")
                            }).error(function (error) {
                                var error_msg = JSON.stringify(error);
                                console.log("Error = " + error_msg);
                                alert(error_msg);
                                reject("Error")
                            });
                    });
                },

                doUpdateProfile: function($scope, data, cId1) {
                    console.log(data);
                    // let cId = $scope.cId;
                    return new Promise(function(resolve, reject) {
                        console.log("Updating profile details.")
                        var url = customer_service_base_url + "/profile/" + cId1;

                        let headers1 = {
                            'Content-Type': 'application/json',
                            'authorization': sStorage.getItem("token"),
                            'Etag': sStorage.getItem("profile_etag")};
                        let options = { headers: headers1 };

                        $http.put(url, data, options).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))
                                resolve("OK")
                            }).error(function (error) {
                                var error_msg = JSON.stringify(error);
                                console.log("Error = " + error_msg);
                                alert(error_msg);
                                reject("Error")
                            });
                    });
                    
                },

                doCreateProfile: function(data) {
                    console.log(data);
                    return new Promise(function(resolve, reject) {
                        console.log("Updating profile details.")
                        var url = customer_service_base_url + "/profile";

                        $http.post(url, data).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))
                                resolve("OK")
                            }).error(function (error) {
                                var error_msg = JSON.stringify(error);
                                console.log("Error = " + error_msg);
                                alert(error_msg);
                                reject("Error")
                            });
                    });
                    
                },

                getProfileData: function($scope, cId) {
                    console.log('fegfrg' + $scope);
                    // let cId = "B5E18BC4-5339-47C5-FBB1-AC9B59251DB7";
                    return new Promise(function(resolve, reject) {
                        console.log("Getting profile details.")
                        var url = customer_service_base_url + "/profile/" + cId;
                        let headers1 = {
                            'Content-Type': 'application/json',
                            'authorization': sStorage.getItem("token"),
                            'Etag':  sStorage.getItem("profile_etag") };
                        let options = { headers: headers1 };

                        $http.get(url, null, options).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4));



                                let data_list = rsp['response'];
                                console.log("fegfg4rg4thy5h" + data_list);
                                sStorage.setItem("profile_etag", rsp['headers']['Etag']);
                                for(var i = 0; i < data_list.length; i++) {
                                    console.log(i);
                                    console.log(data_list[i]);
                                    if(data_list[i]['subtype'] == 'Home') {
                                        if(data_list[i]['type'] == 'Telephone') $scope.homePhoneUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Email') $scope.homeEmailUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Address') $scope.homeAddressUpdate = data_list[i]['value'];
                                    }
                                    if(data_list[i]['subtype'] == 'Work') {
                                        if(data_list[i]['type'] == 'Telephone') $scope.officePhoneUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Email') $scope.officeEmailUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Address') $scope.officeAddressUpdate = data_list[i]['value'];
                                    }
                                    if(data_list[i]['subtype'] == 'Other') {
                                        if(data_list[i]['type'] == 'Telephone') $scope.otherPhoneUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Email') $scope.otherEmailUpdate = data_list[i]['value'];
                                        if(data_list[i]['type'] == 'Address') $scope.otherAddressUpdate = data_list[i]['value'];
                                    }
                                }
                                // $scope.$apply();
                                resolve("OK")
                            }).error(function (error) {
                                var error_msg = JSON.stringify(error);
                                console.log("Error = " + error_msg);
                                alert(error_msg);
                                // reject(error_msg)
                                reject(404);
                            });
                    });
                    
                }
            }
        }
    ])
})();

function getHashParams(paramName){
    console.log("inside the function");
    var hash = window.location.hash;
    if(hash.length > 4){
      hash_sign_idx = hash.lastIndexOf("#");
      hash = hash.substr(hash_sign_idx+1)
      var array = hash.split("&");
      var values, formData = {};
      for (var i = 0; i < array.length; i += 1) {
          values = array[i].split("=");
          formData[values[0]] = values[1];
      }
      console.log("id_token=");
      console.log(formData['id_token']);
      return formData[paramName];
    }
  }


  function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    var plain_token = JSON.parse(window.atob(base64));
    return plain_token;
  };
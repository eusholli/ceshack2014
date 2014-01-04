/*global io MediaServices Phono*/
(function () {
    // Utils and references
    var root = this,
        att = {},
        cache = {};

    // global utils
    var _ = att.util = {
        _uuidCounter: 0,
        uuid: function () {
            return Math.random().toString(16).substring(2) + (_._uuidCounter++).toString(16);
        },
        slice: Array.prototype.slice,
        isFunc: function (obj) {
            return Object.prototype.toString.call(obj) == '[object Function]';
        },
        extend: function (obj) {
            this.slice.call(arguments, 1).forEach(function (source) {
                if (source) {
                    for (var prop in source) {
                        obj[prop] = source[prop];
                    }
                }
            });
            return obj;
        },
        each: function (obj, func) {
            if (!obj) return;
            if (obj instanceof Array) {
                obj.forEach(func);
            } else {
                for (var key in obj) {
                    func(key, obj[key]);
                }
            }
        },
        getQueryParam: function (name) {
            // query string parser
            var cleaned = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]"),
                regexS = "[\\?&]" + cleaned + "=([^&#]*)",
                regex = new RegExp(regexS),
                results = regex.exec(window.location.search);
            return (results) ? decodeURIComponent(results[1].replace(/\+/g, " ")) : undefined;
        },
        // used to try to determine whether they're using the ericsson leif browser
        // this is not an ideal way to check, but I'm not sure how to do it since
        // leif if pretty much just stock chromium.
        h2sSupport: function () {
            // first OR is for original leif
            // second OR is for Mobile bowser
            // third OR is for IIP Leif
            return window.navigator.userAgent == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.4 (KHTML, like Gecko) Chrome/19.0.1077.0 Safari/536.4" ||
            window.navigator.userAgent == "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10A523" ||
            window.webkitPeerConnection00 && window.navigator.userAgent.indexOf('Chrome/24') !== -1;
        },
        getMe: function (token, cb) {
            var self = this,
                baseUrl = "https://auth.tfoundry.com",
                data = {
                    access_token: token
                },
                version;

            // short circuit this if we've already done it
            if (cache.me) {
                // the return is important for halting execution
                return cb(cache.me);
            }

            // removes domain from number if exists
            function cleanNumber(num) {
                return num.split('@')[0];
            }

            // we try to figure out what endpoint this user
            // should be using based on a series of checks.
            console.log(data);

            // first we get the user object
            $.ajax({
                data: data,
                dataType: 'json',
                url: baseUrl + '/me.json',
                success: function (user) {
                    // store the user in the cache
                    cache.me = user;
                    // now we check to see if we've got a webrtc.json specified for this
                    // user.
                    $.ajax({
                        data: data,
                        dataType: 'json',
                        url: baseUrl + '/users/' + user.uid + '/api_services/webrtc.json',
                        // if we get a 200
                        success: function (res) {
                            // if we've got an explicit version use it.
                            var explicitVersion = res && res.version,
                                explicitNumber = res && res.options && res.options.phone_number;
                            if (explicitVersion) {
                                user.version = 'a' + explicitVersion;
                            } else {
                                user.version = 'a1';
                            }
                            user.number = explicitNumber || user.phone_number;                            
                            cb(user);
                        }
                    });
                }
            });
        }
    };


    var message = {};
    
    //place holder for developer's callback function for getMessages and getMessage method
    var getMessagesCallback;
    
    //place holder for developer's callback function for search by number
    var searchByNumberCallback;
    
    //var messageServiceUrl = "https://api.tfoundry.com/a1/messages/messages/";
    var messageServiceUrl = "https://api.foundry.att.com/a1/messages/messages/";
    
    // helper function that creates data returned to developer's callback function
    message.constructReturnData = function(data, textStatus) {
    	var returnData = {};
    	returnData.status = textStatus;
    	returnData.data = data;
    	return JSON.stringify(returnData);
    };
    
    message.sendMessageSuccess = function(data, textStatus, jqXHR) {
    	console.debug("success sendMessage. textStatus = "+textStatus);
    };
    
    message.sendMessageError = function(data, textStatus, jqXHR) {
    	console.error("error sendMessage. textStatus = " + textStatus);
    	console.error(JSON.stringify(data));
    };
    
    message.getMessagesSuccess = function(data, textStatus, jqXHR) {
    	console.debug("success getMessages. textStatus = "+textStatus);
    
    	getMessagesCallback(message.constructReturnData(data, textStatus));
    };
    
    message.getMessagesError = function(data, textStatus, jqXHR) {
    	console.error("error getMessages. textStatus = "+textStatus);
    	console.error(JSON.stringify(data));
    
    	getMessagesCallback(message.constructReturnData(data, textStatus));	
    };
    
    message.deleteMessageSuccess = function(data, textStatus, jqXHR) {
    	console.debug("success deleteMessage. textStatus = "+textStatus);
    };
    
    message.deleteMessageError = function(data, textStatus, jqXHR) {
    	console.error("error deleteMessage. textStatus = "+textStatus);
    	console.error(JSON.stringify(data));
    };
    
    message.searchByNumberSuccess = function(data, textStatus, jqXHR) {
    	console.debug("success searchByNumber. textStatus = "+textStatus);
    
    	searchByNumberCallback(message.constructReturnData(data, textStatus));	
    };
    
    
    message.searchByNumberError = function(data, textStatus, jqXHR) {
    	console.error("error searchByNumber. textStatus = "+textStatus);
    	console.error(JSON.stringify(data));
    	
    	searchByNumberCallback(message.constructReturnData(data, textStatus));	
    };
    
    // helper function that gets URL, appends access token
    message.getUrl = function(requestedPath) {
    	var access_token = window.att.config.apiKey;
    	var url = "";
    	
    	if(requestedPath) {
    		url = messageServiceUrl+requestedPath+"/?access_token="+access_token;
    	} else {
    		url = messageServiceUrl+"?access_token="+access_token;		
    	}
    	
    	console.debug("url = "+url);
    	
    	return url;	
    };
    
    message.sendMessage = function(recipient, text) {
    	console.debug('sending message '+text+' to '+recipient);
    
    	var data = {};
    	data.recipient = recipient;
    	data.text = text;
    
    	$.ajax({
    		type : 'POST',
    		url : message.getUrl(),
    		data : JSON.stringify(data),
    		success : message.sendMessageSuccess,
    		error : message.sendMessageError,
    		dataType : 'application/json'
    	});
    };
    
    message.getMessages = function(callback) {
    	getMessagesCallback = callback;
    	$.ajax({
    		type : 'GET',
    		url : message.getUrl(),
    		success : message.getMessagesSuccess,
    		error : message.getMessagesError
    	});
    };
    
    message.getMessage = function(messageId, callback) {
    	getMessagesCallback = callback;
    	$.ajax({
    		type : 'GET',
    		url : message.getUrl(messageId),
    		success : message.getMessagesSuccess,
    		error : message.getMessagesError
    	});
    };
    
    message.deleteMessage = function(messageId) {
    	$.ajax({
    		type : 'DELETE',
    		url : message.getUrl(messageId),
    		success : message.deleteMessageSuccess,
    		error : message.deleteMessageError
    	});
    };
    
    message.searchByNumber = function(number, callback) {
    	searchByNumberCallback = callback;
    	$.ajax({
    		type : 'GET',
    		url : message.getUrl("filter/"+number),
    		success : message.searchByNumberSuccess,
    		error : message.searchByNumberError
    	});
    };
    
    att.message = message;
    





    // attach to window or export with commonJS
    if (typeof exports !== 'undefined') {
        module.exports = att;
    } else {
        // make sure we've got an "att" global
        root.ATT || (root.ATT = {});
        _.extend(root.ATT, att);
    }

}).call(this);

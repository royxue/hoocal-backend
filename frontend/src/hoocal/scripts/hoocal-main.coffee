app = angular.module 'hoocal', ['ngMaterial', 'angular-md5', 'ngRoute']

app.config ['$routeProvider', ($routeProvider) ->
  $routeProvider
    .when '/login/', {
      templateUrl: 'login.tpl.html'
      controller: 'hcLogin'
    }
    .when '/main/', {
      templateUrl: 'main.tpl.html'
      controller: 'hcMain'
    }
    .otherwise {
      templateUrl: 'not-found.tpl.html'
      controller: 'hcRoute'
    }
]


app.service 'hcsConfig', [() ->
  if localStorage.hc_debug == 'true'
    @debug = true
  else
    @debug = false

  # Can be rewritten by the localStorage.hc_server_url
  if typeof(localStorage.hc_server_url) == 'string'
    @server_url = localStorage.hc_server_url
  else
    # @server_url = 'http://172.27.220.128:8000/'
    @server_url = 'https://hoocal.herokuapp.com/'

  @auth_field = 'X-Hoocal-Token'

  # The modules subpath
  @module_path = {
    root: ''
    hoocal: 'hoocal/'
  }

  return
]

# Service hcsUtil, series tools for catchchat
app.service 'hcsUtil', ['$rootScope', 'md5', ($rootScope, md5) ->

  self = @

  # This method used for send event to all angular node
  trigger_sender = $rootScope.$new()
  trigger_sender.$id = 'hcsUtil.trigger_sender'
  @trigger = (event, args) ->
    trigger_sender.$emit event, args
    $rootScope.$broadcast event, args

  now_id = {}
  now_void_id = 0
  @nextId = (type) ->
    if typeof(type) == 'string'
      if angular.isUndefined now_id[type]
        return now_id[type] = 0
      else
        return ++now_id[type]

  @ancestorHasAttribute = (element, attrName, limit) ->
    limit = limit || 4
    current = element
    while limit-- && current.length
      if current[0].hasAttribute && current[0].hasAttribute attrName
        return true
      current = current.parent()
    return false
  
  @isParentDisabled = (element, limit) ->
    return self.ancestorHasAttribute element, 'disabled', limit

  @hoocalEncrypt = (before_str) ->
    return md5.createHash(md5.createHash(before_str) + 'hoocal')

  return
]

# Service csServer, for server varibles
app.service 'hcsServer', ['hcsConfig', (hcsConfig) ->

  @getUrl = (url, module) ->
    if typeof(module) == 'string'
      return hcsConfig.server_url + hcsConfig.module_path[module] + url
    else
      return hcsConfig.server_url + url

  return
]

app.service 'hcsLog', [() ->
  @hire_info = () ->
    console.log(
        '%c hire@hoocal.com',
        'color: #488;'
      )
  @info = (message) ->
    console.log(
        '%c ' + message,
        'color: #686; border-left: solid 2px #686;'
      )
  @error = (message) ->
    console.log(
        '%c ' + message,
        'color: #866; border-left: solid 2px #866;'
      )
  @dir = (varible) ->
    console.dir(varible)

  return
]

app.service 'hcsAuth', ['$http', '$q', 'hcsServer', 'hcsUtil', 'hcsConfig', 'hcsLog', ($http, $q, hcsServer, hcsUtil, hcsConfig, hcsLog) ->
  self = @

  updateAuth = (email, token) ->
    if typeof(email) != 'undefined'
      localStorage.hc_header_token = 'apikey ' + email + ':' + token
      localStorage.hc_email = email
      localStorage.hc_token = token
    if typeof($http.defaults.headers.common[hcsConfig.auth_field]) == 'undefined' && typeof(localStorage.hc_header_token) != 'undefined'
      $http.defaults.headers.common[hcsConfig.auth_field] = localStorage.hc_header_token
      hcsUtil.trigger 'hceAuthUpdate', true
    else
      hcsUtil.trigger 'hceAuthUpdate', false
  updateAuth()

  @isAuthOk = () ->
    return typeof($http.defaults.headers.common[hcsConfig.auth_field]) != 'undefined'

  @doAuth = (email, password) ->
    deferred = $q.defer()
    $http
      .post hcsServer.getUrl('auth/'), {email: email, password: hcsUtil.hoocalEncrypt(password)}
      .success (data, status, headers) ->
        hcsLog.info 'Auth: success'
        updateAuth email, headers hcsConfig.auth_field.toLowerCase()
        deferred.resolve()
      .error (data, status) ->
        hcsLog.error 'Auth: error code: ' + status
        deferred.reject 'Auth: error code: ' + status
    return deferred.promise

  @create = (email, password, nickname) ->
    deferred = $q.defer()
    $http
      .post hcsServer.getUrl('user/', 'hoocal'), {email: email, password: hcsUtil.hoocalEncrypt(password), nickname: nickname}
      .success (data, status, headers) ->
        hcsLog.info 'Register: success'
        promise = self.doAuth email, password
        promise.finally () ->
          deferred.resolve()
      .error (data, status) ->
        hcsLog.error 'Register: error code: ' + status
        deferred.reject 'Register: error code: ' + status
    return deferred.promise

  @clear = () ->
    delete localStorage.hc_header_token
    delete localStorage.hc_token
    delete localStorage.hc_id
    delete $http.defaults.headers.common[hcsConfig.auth_field]
    hcsUtil.trigger 'hceAuthClear', true
    hcsLog.info 'Auth: clear'

  return
]


app.directive 'hcdApp', ['$location', 'hcsAuth', 'hcsUtil', ($location, hcsAuth, hcsUtil) ->
  return {
    restrict: 'A'
    link: (scope, element, attrs) ->
      toggleSceneState = (is_auth_ok) ->
        if is_auth_ok
          $location.url '/main/'
        else
          $location.url '/login/'
      scope.$on 'hceAuthUpdate', toggleSceneState
      scope.$on 'hceRouteGuide', () ->
        toggleSceneState hcsAuth.isAuthOk()
      hcsUtil.trigger 'hceRouteGuide'
        
  }
]

app.directive 'hcdCalendar', [() ->
  return {
    restrict: 'EA'
    link: (scope, element, attrs) ->
      calendar = $(element).find '.hc-calendar'
      calendar.fullCalendar {
        header: false
        editable: true
        theme: true
        contentHeight: 500
      }
      scope.$on 'hceCalendarUpdate', (event, data) ->
        console.dir data
        events = []
        for event in data
          events.push {
            start: new Date event.start_time*1000
            end: new Date event.end_time*1000
            title: event.title
            id: event.id
          }
        console.dir events
        
        calendar.fullCalendar 'removeEvents'
        calendar.fullCalendar 'addEventSource', {
            events: events
          }
  }
]

app.directive 'hcdFillHeight', [() ->
  return {
    restrict: 'EA'
    link: (scope, element, attrs) ->
      $(window)
        .resize () ->
          $(element).height $(element).parent().height()
        .resize()
  }
]


app.controller 'hcMain', ['hcsUtil', '$http', 'hcsServer', 'hcsLog', '$scope', '$mdDialog', (hcsUtil, $http, hcsServer, hcsLog, $scope, $mdDialog) ->
  hcsUtil.trigger 'hceRouteGuide'
  $scope.edit_show = false
  $scope.current_event = {}

  $http
    .get hcsServer.getUrl('event/', 'hoocal')
    .then(
        (data) ->
          hcsUtil.trigger 'hceCalendarUpdate', data.data.objects
        (data, status) ->
          hcsLog.error 'Get event failed, code: ' + status
      )
  $scope.moxtra = () ->
    window.get_token()

  $scope.$on 'hceEditEvent', (event, data) ->
    console.dir data
    $scope.current_event = data
    # $mdDialog.show {
    #   templateUrl: 'edit-dialog.tpl.html'
    #   controller: 'hcEditEvent'
    #   parent: $('body')[0]
    # }
    $scope.edit_show = true

  return
]
app.controller 'hcEditEvent', [() ->
]

app.controller 'hcRoute', ['hcsUtil', (hcsUtil) ->
  hcsUtil.trigger 'hceRouteGuide'
  return
]

app.controller 'hcLogin', ['$route', '$scope', '$mdToast', 'hcsAuth', 'hcsUtil', ($route, $scope, $mdToast, hcsAuth, hcsUtil) ->
  hcsUtil.trigger 'hceRouteGuide'
  $scope.tab_selected = 0
  # hcsAuth.doAuth 'royxue@gmail.com', 'hoocal'

  $scope.pl_login = false
  login = (email, password) ->
    if !$scope.pl_login && email && password
      $scope.pl_login = true
      promise = hcsAuth.doAuth email, password
      promise.finally () ->
        $scope.pl_login = false
      promise.then(
          () ->
            return
          () ->
            $mdToast.show {
              template: '<md-toast>Check your E-mail and password please.</md-toast>'
              hideDelay: 2000
              controllerAs: 'hcLogin'
              position: 'top right'
            }
        )
  $scope.login = login

  $scope.pl_register = false
  register = (email, password, nickname) ->
    if !$scope.pl_register && email && password && nickname
      $scope.pl_register = true
      promise = hcsAuth.create email, password, nickname
      promise.finally () ->
        $scope.pl_register = false
      promise.then(
          () ->
            return
          () ->
            $mdToast.show {
              template: '<md-toast>Sorry, this email has been registered.</md-toast>'
              hideDelay: 2000
              controllerAs: 'hcLogin'
              position: 'top right'
            }
        )
  $scope.register = register


  return
]

app.controller 'hcMainSidenav', ['$scope', 'hcsUtil', ($scope, hcsUtil) ->
  $scope.events = []
  $scope.$on 'hceCalendarUpdate', (event, data) ->
    $scope.events = data
  $scope.editEvent = (event) ->
    hcsUtil.trigger 'hceEditEvent', event
]
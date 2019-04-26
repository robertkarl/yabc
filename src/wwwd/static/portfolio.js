(function() {
  var User = Backbone.Model.extend({
      url :   '/yabc/v1/users'
  });
  var user = new User();
  user.save();
  console.log(user);
})();

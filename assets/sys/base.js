/**
 * Created by yufengzhang210851 on 2016-08-12.
 */
$.fn.extend({

});
$.extend({
    majax: function(method, url, callback){
        $.ajax({
            type: method,
            url: url,
            success: function(data){
                callback(data);
            }
        });
    }
});
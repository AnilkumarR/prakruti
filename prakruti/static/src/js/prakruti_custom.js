openerp.Plant = function (instance) {
    instance.Plant = {
        value_true: true,
        SomeType: instance.web.Class.extend({
            init: function (value) {
                this.value = value;
            }
        })
    };
};
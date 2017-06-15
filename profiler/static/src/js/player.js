odoo.define('web.profiler', function (require) {
"use strict";
var Widget = require('web.Widget');
var SystrayMenu = require('web.SystrayMenu');
//var session = require('web.session');

var Player = Widget.extend({
        template: 'profiler.player',
        events: {
            "click .profiler_enable": "enable",
            "click .profiler_disable": "disable",
            "click .profiler_clear": "clear",
            "click .profiler_dump": "dump",
        },
        apply_class: function(css_class) {
            console.log(css_class)
            this.$el.removeClass('profiler_player_enabled');
            this.$el.removeClass('profiler_player_disabled');
            this.$el.removeClass('profiler_player_clear');
            this.$el.addClass(css_class);
        },
        enable: function() {
            this.rpc('/web/profiler/enable', {});
            this.apply_class('profiler_player_enabled');
        },
        disable: function() {
            this.rpc('/web/profiler/disable', {});
            this.apply_class('profiler_player_disabled');
        },
        clear: function() {
            this.rpc('/web/profiler/clear', {});
            this.apply_class('profiler_player_clear');
        },
        dump: function() {
            $.blockUI();
            this.session.get_file({
                url: '/web/profiler/dump',
                complete: $.unblockUI
            });
        },
    });

SystrayMenu.Items.push(Player);

});

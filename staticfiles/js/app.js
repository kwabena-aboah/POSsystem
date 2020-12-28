$(document).ready(function() {
     $('#resetcashpopover').popover({html:true});
 });

 $('#CodeModal').on('shown.bs.modal', function (e) {
     $('#codeInput').focus();
 })

 var app = new Vue({
     delimiters: ['[[', ']]'],
     el: '#app',
     data: {
         order: {},
         items: [],
         cashgot: 0.0
     },
     methods: {
         update_order: function() {
             fetch("/api/orders/current/")
                 .then(res => res.json())
                 .then((out) => {
                     this.order = out;
                 });
         },
         update_items: function() {
             fetch("/api/orders/current/items/")
                 .then(res => res.json())
                 .then((out) => {
                     this.items = out;
                 });
         },
         cashmodal: function() {
             $('#cashgot').focus();
             console.log(this.order.total_price);
             document.getElementById('topay').value = this.order.total_price;
         },
         removeProduct: function(product_id) {
             fetch("/api/orders/current/items/" + encodeURIComponent(product_id) + "/", {method: 'DELETE'})
                 .then(response => {
                     if (response.status == 200) {
                         response.json().then(json => {
                             this.items = json;
                         });
                         this.update_order();
                     } else {
                         window.alert("Can't remove product");
                         console.log(response);
                     }
                 });
         },
         addProduct: function(product_id) {
             fetch("/api/orders/current/items/" + encodeURIComponent(product_id) + "/", {method: 'PUT'})
                 .then(response => {
                     if (response.status == 404) {
                         window.alert("Product not found");
                     } else if (response.status != 200) {
                         console.log(response);
                         window.alert("Product out of stock. Refill please!");
                     } else {
                         this.update_order();
                         // this must be a promise
                         response.json().then(json => {
                             this.items = json;
                         });
                     }
                 });
         },
         resetCash: function() {
             var value = document.getElementById('resetcashinput').value;
             fetch("/cash/" + encodeURIComponent(value))
                 .then(response => {
                     if (response.status != 200) {
                         window.alert("Can't reset cash");
                         console.log(response);
                     } else {
                         $('#cashresetamount').text(encodeURIComponent(value));
                         $('#cashresetdiv').show()
                         $('#resetcashpopover').popover('hide');
                     }
                 });
         },
         payed: function(method) {
             if (confirm("Do you want to print the addition?")) {
                 console.log(this.order.id);
                 window.open("/print-order/" + this.order.id, "_blank").focus();
             }

             if (method == "cash") {
                 fetch("/api/pay/cash/").then(response => {
                     if (response.status != 200) {
                         window.alert("Couldn't pay");
                         console.log(response);
                     } else {
                         response.json().then(json => {
                             window.alert("Added " + json.added + " to the register");
                         });
                         this.update_order();
                         this.update_items();
                     }
                 });
             } else if (method == "momo") {
                 if (!confirm('Are you sure?'))
                     return;
                 fetch("/api/pay/momo/").then(response => {
                     if (response.status != 200) {
                         window.alert("Couldn't pay");
                         console.log(response);
                     } else {
                         window.alert("Successfully paid.");
                         this.update_order();
                         this.update_items();
                     }
                 });
             }
             console.log("Person payed");
         },
         scanCode: function() {
             this.addProduct(document.getElementById('codeInput').value);
             document.getElementById('codeInput').value = "";
             document.getElementById('codeInput').focus();
         },
         reset: function() {
             fetch("/api/orders/current/", {method: 'delete'})
                 .then(response => {
                     if (response.status == 200) {
                         window.alert("Order cleared");
                     } else {
                         window.alert("Can't clear order");
                         console.log(response);
                     }
                 });
             this.update_order();
             this.update_items();
         }
     },
     created() {
         this.update_order();
         this.update_items();
     }
 });

 $('#cashModal').on('shown.bs.modal', function() {
     app.cashmodal();
 });

 $(document).ready(function() {
     // This shallst load /addition in its div
     $('#resetcashpopover').popover({html:true});
 });

 $('#CodeModal').on('shown.bs.modal', function (e) {
     $('#codeInput').focus();
 })
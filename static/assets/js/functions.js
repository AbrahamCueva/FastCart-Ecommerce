$(document).ready(function() {
    const Toast = Swal.mixin({
        toast: true,
        position: "top",
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true,
    });

    function generateCartId() {
        let cartId = localStorage.getItem('cartId');
        if (cartId === null) {
            cartId = "";
            for (let i = 0; i < 10; i++) {
                cartId += Math.floor(Math.random() * 10);
            }
            localStorage.setItem('cartId', cartId);
        }
        return cartId;
    }

    $(document).on('click', '.add_to_cart', function() {
        const button_el = $(this);
        const id = button_el.attr("data-id");
        const qty = $(".quantity").val() || 1;
        const size = $("input[name='size']:checked").val() || "default";
        const color = $("input[name='color']:checked").val() || "default";
        const cart_id = generateCartId();
        console.log("size: ", size);
        console.log("color: ", color);        

        $.ajax({
            url: "/add_to_cart/",
            data: {
                id: id,
                qty: qty,
                size: size,
                color: color,
                cart_id: cart_id,
            },
            beforeSend: function() {
                button_el.html("<i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response) {
                console.log(response);
                Toast.fire({
                    icon: 'success',
                    title: response?.message,
                });
                button_el.html("<i class='fi-rs-shopping-cart ms-2'></i>");
                $('.total_cart_items').text(response?.total_cart_items);
            },
            error: function(xhr) {
                console.log("Error status: ", xhr.status); 
                console.log("Response Text: ", xhr.responseText); 

                let errorResponse;
                try {
                    errorResponse = JSON.parse(xhr.responseText);
                } catch {
                    errorResponse = { error: "Ocurrió un error inesperado." };
                }

                Toast.fire({
                    icon: 'error',
                    title: errorResponse?.error,
                });
            }
        });
    });

    $(document).on('click', '.update_cart_qty', function() {
        const button_el = $(this);
        const update_type = button_el.attr("data-update_type");
        const item_id = button_el.attr("data-item_id");
        const product_id = button_el.attr("data-product_id");
        var qty = $(".item-qty-" + item_id).val()
        const cart_id = generateCartId();

        if(update_type === "increase") {
            $(".item-qty-" + item_id).val(parseInt(qty) + 1);
            qty++;
        } else {
            if(parseInt(qty) <= 1) {
                $(".item-qty-" + item_id).val(1);
                qty = 1;
            } else {
                $(".item-qty-" + item_id).val(parseInt(qty) - 1);
                qty--;
            }
        }
        $.ajax({
            url: "/add_to_cart/",
            data: {
                id: product_id,
                qty: qty,
                cart_id: cart_id,
            },
            beforeSend: function() {
                button_el.html("<i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response) {
                console.log(response);
                Toast.fire({
                    icon: 'success',
                    title: response?.message,
                });
                if(update_type === "increase") {
                    button_el.html("+")
                } else {
                    button_el.html("-")
                }
                $(".item_sub_total_" + item_id).text(response.item_sub_total)
                $(".cart_sub_total").text(response.cart_sub_total)
            },
            error: function(xhr) {
                console.log("Error status: ", xhr.status); 
                console.log("Response Text: ", xhr.responseText); 

                let errorResponse;
                try {
                    errorResponse = JSON.parse(xhr.responseText);
                } catch {
                    errorResponse = { error: "Ocurrió un error inesperado." };
                }

                Toast.fire({
                    icon: 'error',
                    title: errorResponse?.error,
                });
            }
        });
    });

    $(document).on("click", ".delete_cart_item", function() {
        const button_el = $(this);
        const item_id = button_el.attr("data-item_id");
        const product_id = button_el.attr("data-product_id");
        const cart_id = generateCartId();

        $.ajax({
            url: "/delete_cart_item/",
            data: {
                id: product_id,
                item_id: item_id,
                cart_id: cart_id,
            },
            beforeSend: function() {
                button_el.html("<i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response) {
                console.log(response);
                Toast.fire({
                    icon: 'success',
                    title: response?.message,
                });
                $('.total_cart_items').text(response?.total_cart_items);
                $('.cart_sub_total').text(response?.cart_sub_total);
                $('.item_div_' + item_id).remove();
            },
        })
    })

    $(document).on("click", ".add_to_wishlist", function() {
        const button = $(this)
        const product_id = button.attr("data-product_id")
        console.log(product_id)
        $.ajax({
            url: `/customer/add_to_wishlist/${product_id}`,
            beforeSend: function() {
                button.html("<i class='fa-solid fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response) {
                button.html("<i class='fi-rs-heart'></i>")
                console.log(response)
                if(response.message === "No estás logueado") {
                    Toast.fire({
                        icon: "warning",
                        title: response.message
                    })
                } else {
                    Toast.fire({
                        icon: "success",
                        title: response.message
                    })
                }
            },
            error: function() {
                button.html("<i class='fi-rs-heart'></i>")
            }
        })
    })
});



/*
	

*/

function addItemToList(form_id, container_id, product, qty){
	let form = document.getElementById(form_id)
	let list = document.getElementById(container_id)
	let prod = document.getElementById(product).value
	let quantity = document.getElementById(qty).value
	let listItem = document.createElement('span')
	listItem.innerText = String(list.children.length+1)+'.    ' + prod + ' x' + String(quantity)
	listItem.classList.add('listing-item')
	list.appendChild(listItem)

	let prod_val = document.createElement('input')
	prod_val.type = "hidden"
	prod_val.name = "resource"
	prod_val.value = `${prod}:-:${quantity}`
	form.appendChild(prod_val)
}


function showAdder(id){
	$('#'+id).addClass('open')
}



function hideAdder(id){
	$('#'+id).removeClass('open')
}
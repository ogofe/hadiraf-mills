/*
	GLOBALS
	LICENSE: MIT
*/



function newsletterSignup(event){
    event.preventDefault()
    console.log(event.target)
    Email.send({
        Host: "smtp.gmail.com",
        Username: "noreply.abknown@gmail.com",
        Password: "Lyoko22ll",
        To: $("#letter-email").val(),
        From: "noreply.abknown@gmail.com",
        Subject: "Newsletter From Sub Saharan Development",
        Body: `Hello ${$('#letter-name').val()}, 
                \n You have been subscribed to the sub saharan development fund newsletter.`,
    })
}

function submitForm(){
    event.preventDefault();
    document.title = "Sub Saharan Development Fund Applicant Form"
    document.querySelector('.overlay').classList.remove('d-none')

    setTimeout(
        () => {
            document.querySelector('.overlay').classList.add('d-none')
            document.querySelector('.modal').classList.remove('d-none')
            },
            2800
        )
        let btn1 = document.getElementById('print')
        let btn2 = document.getElementById('input')
        btn2.style.display = 'none';
        btn1.style.display = 'none';
        Email.send({
        Host: "smtp.gmail.com",
        Username: "noreply.abknown@gmail.com",
        Password: "Lyoko22ll",
        To: $("#letter-email").val(),
        From: "noreply.abknown@gmail.com",
        Subject: "Newsletter From Sub Saharan Development",
        Body: `Hello ${$('#letter-name').val()}, 
                Dear ${document.getElementById('fname').value}, your application for the sub saharan development fund grant has been successfully received.`,
    })
}


function printform(){
    document.querySelector('.modal').classList.add('d-none')
    setTimeout(() => {
        window.print()
        .then(res => console.log("After Print",res))
    }, 700)
}

function setImage(){
    let file = event.target.files[0]
    let url = URL.createObjectURL(file)
    document.querySelector('#img').setAttribute('src', url)
}

document.querySelector('#letter').addEventListener("submit", newsletterSignup)
$('#input').on("input", setImage)


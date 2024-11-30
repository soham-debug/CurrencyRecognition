let englishtext = "";
let hinditext = "";

window.onload = () => {
	$('#sendbutton').click(() => {
		englishtext = "";
		hinditext = "";
		hideInterface();

		imagebox = $('#imagebox1')
		input = $('#imageinput')[0]
		if(input.files && input.files[0])
		{
			let formData = new FormData();
			formData.append('image' , input.files[0]);
			$.ajax({
				url: "/detectObject", 
				// fix below to your liking
				// url: "http://xxx.xxx.xxx.xxx:8080/detectObject", 
				type:"POST",
				data: formData,
				cache: false,
				processData:false,
				contentType:false,
				error: function(data){
					console.log("upload error" , data);
					console.log(data.getAllResponseHeaders());

					updateInterface();
				},
				success: function(data){
					console.log(data);
					bytestring = data['status'];
					image = bytestring.split('\'')[1];
					englishtext = data['englishmessage'];
					hinditext = data['hindimessage'];
					imagebox2 = $('#imagebox2')
					imagebox2.attr('src' , 'data:image/jpeg;base64,'+image);
					
					// $('#audio').html('<audio autoplay><source src="static/detected_image.mp3"></audio>');
					updateInterface();					
				}
			});
			
		}
	});

	// below speechSynthesis WebAPI
	const voiceEnglishOutputButton = document.getElementById('voice-english-output');
	const voiceHindiOutputButton = document.getElementById('voice-hindi-output');
	voiceEnglishOutputButton.addEventListener('click', () => {
		let utterance = new SpeechSynthesisUtterance(englishtext);
		// utterance.lang = "en-US";
		utterance.lang = "en-GB";
		// utterance.voice = speechSynthesis.getVoices()[2]; // MS Zira
		// utterance.voice = speechSynthesis.getVoices()[4]; // Google English
		utterance.voice = speechSynthesis.getVoices()[5];// Google English Female
		speechSynthesis.speak(utterance);
	});
	voiceHindiOutputButton.addEventListener('click', () => {
		let utterance = new SpeechSynthesisUtterance(hinditext);
		utterance.lang = "hi-IN";
		utterance.voice = speechSynthesis.getVoices()[10];// Google Hindi Female
		speechSynthesis.speak(utterance);
	});
};



function readUrl(input){
	imagebox = $('#imagebox1');
	console.log("evoked readUrl");
	if(input.files && input.files[0]){
		let reader = new FileReader();
		reader.onload = function(e){
			// console.log(e)
			imagebox.attr('src',e.target.result); 
		}
		reader.readAsDataURL(input.files[0]);
	}
}


function hideInterface(){
	$("#voice-english-output").hide();
	$("#voice-hindi-output").hide();
}

function updateInterface(){
	$("#voice-english-output").show();
	$("#voice-hindi-output").show();
}

function changeColor(){
	let sendButton = document.querySelector("#sendbutton");
	sendButton.style.backgroundColor = "orange";
	sendButton.style.color = "black";
}

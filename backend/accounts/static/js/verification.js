const inputs = document.querySelectorAll(".otp-inputs input");

    inputs.forEach((input, index) => {
      input.addEventListener("input", () => {
        if (input.value.length === 1 && index < inputs.length - 1) {
          inputs[index + 1].focus();
        }
      });

      input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !input.value && index > 0) {
          inputs[index - 1].focus();
        }
      });
    });


    function setRealVH() {
      let vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    window.addEventListener('resize', setRealVH);
    window.addEventListener('load', setRealVH);

    

    // function submitOTP() {
    //   const otp = Array.from(inputs).map(input => input.value).join('');
    //   if (otp.length === 4) {
        
    //     // Send to backend here if needed
    //   } else {
    //     alert("Please enter all 4 digits.");
    //   }
    // }
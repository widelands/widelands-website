/* Functions to hide some elements on small viewports */
$( function() {
    $( "#toggleMenu" ).on( "click", function() {
          $( ".respMenuHidden" ).toggle( "slow" );
    });
});

$( function() {
    $( "#respLoginButton" ).on( "click", function() {
          $( "#responsiveLogin" ).toggle( "slow" );
    });
});

$( function() {
    $( "#respAsideButton" ).on( "click", function() {
          $( ".columnModule" ).toggle( "slow" );
    });
});

/*
    Buttons for devices which have no hover functionality. Taken from:
	https://wiki.selfhtml.org/wiki/Navigation/Dropdown-Men%C3%BC#inklusives_Dropdown-Men.C3.BC
*/
document.addEventListener('DOMContentLoaded', function () {
	dropdownExtension();

	function dropdownExtension() {
		const submenus = document.querySelectorAll('nav li > ul');
		for (let submenu of submenus) {
			submenu.classList.add('submenu');
			submenu.insertAdjacentHTML('beforebegin',
				`
			<button aria-expanded="false">
				<span class="visually-hidden">Open submenu</span>
				<img src="/static/img/menu_expand.png">
			</button>
		`
			);
		}
		document.documentElement.addEventListener('click', event => {
			if (event.target.tagName == 'BUTTON' && event.target.hasAttribute(
					'aria-expanded')) {
				event.target.setAttribute('aria-expanded', event.target.getAttribute(
					'aria-expanded') != 'true');
				event.target.nextElementSibling.classList.toggle('visible');
			}
		});
		document.addEventListener('keyup', (event) => {
			if (event.key === 'Escape') {
				hideSubmenu();
			}
			if ((event.key === 'Tab') && (!event.target.closest('.visible'))) {
				hideSubmenu();
			}
		});

		function hideSubmenu() {
			let elements = document.querySelectorAll('.visible');
			elements.forEach(function (element) {
				element.classList.remove('visible');
			});
			let buttons = document.querySelectorAll('[aria-expanded="true"]');
			buttons.forEach(function (button) {
				button.setAttribute('aria-expanded', 'false');
			});
		}
	}
});

/*
function toggleHidden(cl) {
  var x = document.getElementsByClassName(cl);
  */
/*if (x.className === "topnav") {
    x.className += " responsive";
  } else {
    x.className = "topnav";
  }*//*

}
*/

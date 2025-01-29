/* Functions to show/hide some elements on small viewports */

/* Main menu */
$( function() {
    $( "#toggleMenu" ).on( "click", function() {
          $( ".respMenuHidden" ).toggle( "slow" );
    });
});
/* Login */
$( function() {
    $( "#respLoginButton" ).on( "click", function() {
          $( "#responsiveLogin" ).toggle( "slow" );
    });
});
/* Aside = Polls, Important dates and Latest posts */
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

  /* Add buttons into DOM */
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

    /* Add the click event to button */
		document.documentElement.addEventListener('click', event => {
		  console.log(event.target);
			if ( event.target.tagName == 'BUTTON' && event.target.hasAttribute('aria-expanded') ) {
				event.target.setAttribute( 'aria-expanded', event.target.getAttribute('aria-expanded') != 'true' );
				event.target.nextElementSibling.classList.toggle('visible');
			}
		});

    /* Hide open submenus */
/*		document.addEventListener('mouseover', (event) => {
			if (!event.target.classList.contains('visible')) {
				hideSubmenu();
			}
		});*/

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

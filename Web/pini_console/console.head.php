<?php
if (!defined('_GNUBOARD_')) exit;

$begin_time = get_microtime();

$IS_LOGIN = true;
if($member["mb_id"] == ""){
	$IS_LOGIN = false;
}

include_once(G5_PATH.'/head.sub.php');
?>
<style>
body {
	padding-top: 50px;
}

.box-small{
	padding:5px 5px 5px 5px;
	margin-bottom:5px;
	background-color: #fff;
	border-color:#ddd;
	border-width:1px;
	border-radius:4px 4px 4px 4px; 
	border-style: solid;
	-webkit-box-shadow: none;
	box-shadow: none;
}

#loading-busy-layer {
	position: absolute;
	z-index:300000000;
	left: 0px;
	top: 0px;
	width:100%;
	height:100%;
	background-color: #000;
	opacity: 0.6;
	display: none;
}

.spinner {
	position: absolute;
	width: 30px;
	height: 30px;
	left: 50%;
	top: 50%;
	background-color: #fff;

	-webkit-animation: rotateplane 1.2s infinite ease-in-out;
	animation: rotateplane 1.2s infinite ease-in-out;
}

@-webkit-keyframes rotateplane {
	0% { -webkit-transform: perspective(120px) ; background: white; }
	50% { -webkit-transform: perspective(120px) rotateY(180deg); background: yellow; }
	100% { -webkit-transform: perspective(120px) rotateY(180deg)  rotateX(180deg); background: white; }
}

@keyframes rotateplane {
	0% { 
		background: white; 
		transform: perspective(120px) rotateX(0deg) rotateY(0deg);
		-webkit-transform: perspective(120px) rotateX(0deg) rotateY(0deg)
	} 50% { 
		background: yellow; 
		transform: perspective(120px) rotateX(-180.1deg) rotateY(0deg);
		-webkit-transform: perspective(120px) rotateX(-180.1deg) rotateY(0deg) 
	} 100% { 
		background: white; 
		transform: perspective(120px) rotateX(-180deg) rotateY(-179.9deg);
		-webkit-transform: perspective(120px) rotateX(-180deg) rotateY(-179.9deg);
	}
}
</style>

<script src="http://code.jquery.com/jquery-1.9.1.js"></script>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap-theme.min.css">
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.min.js"></script>
<script src="js/bootstrap-filestyle.min.js"></script>
<script src="js/jquery.form.min.js"></script>

<nav class="navbar navbar-inverse navbar-fixed-top">
	<div class="container">
		<div class="navbar-header">
			<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
				<span class="sr-only">Toggle navigation</span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
			</button>
			<a class="navbar-brand" href="#">PiniConsole(beta)</a>
		</div>
		<div id="navbar" class="collapse navbar-collapse">
			<ul class="nav navbar-nav">
				<li <? if($PINI_CONSOLE_MENU==1){?>class="active"<?}?> ><a href="index.php">메인</a></li>
				<li <? if($PINI_CONSOLE_MENU==2){?>class="active"<?}?> ><a href="builds.php">빌드</a></li>
				<li <? if($PINI_CONSOLE_MENU==3){?>class="active"<?}?> ><a href="share.php">공유</a></li>
				<li <? if($PINI_CONSOLE_MENU==4){?>class="active"<?}?> >
					<a href="login.php">
						<?if($IS_LOGIN){?>
								로그아웃
						<?}else{?>
								로그인
						<?}?>
					</a>
				</li>
			</ul>
		</div><!--/.nav-collapse -->
	</div>
</nav>

<div class="container">
	<div class="starter-template">
		<div id="loading-busy-layer">
			<div class="spinner"></div>
		</div>

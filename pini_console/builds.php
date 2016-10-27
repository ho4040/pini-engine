<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$g5['title'] = '개발자 콘솔';
include_once ('./console.head.php');

$mb_id = $member["mb_id"];
?>
<?
if($IS_LOGIN){
?>
<script>
var currentIdx = -1;
var submitCallback = null;
function openDeleteModal(idx){
	$('#removeModal').modal();
	currentIdx = idx;
}
function openAndroidModal(idx){
	currentIdx = idx;
	$('#loading-busy-layer').show();
	$.ajax({
		url: "android_export_info.php",
		method: "POST",
		data: { idx : idx },
	}).done(function(data) {
		var ret = JSON.parse(data);
		$("#AOS_idx").val(idx);
		$("#AOS_gameName").val(ret["gameName"]);
		$("#AOS_packageName").val(ret["packageName"]);
		$("#AOS_appVersion").val(ret["appVersion"]);
		$("#AOS_keyPassword").val(ret["password"]);
		$("#AOS_icon_display").attr("src",ret["icon"]);
		$("#AOS_keystore").val("");
		$("#AOS_icon").val("");
		if(ret["keystore"])
			$(".AOS-keystore-help-block").html("<font color='green'>이미 업로드된 키스토어가 있습니다.</font>");
		else
			$(".AOS-keystore-help-block").html("사용중인 키스토어가 있을 시 업로드해주세요.");
		if(ret["apkpath"]){
			$("#apkDownload").css("display","initial");
		}else{
			$("#apkDownload").css("display","none");
		}
		$('#loading-busy-layer').hide();
		$('#androidConfigureModal').modal();
	});
}
function saveAndroidModel(){
	$('#AOS_Settings').submit();
}
function _apkDownload(){
	document.location.href="android_export_download.php?idx="+currentIdx;
}
function checkAndroidExport(){
	submitCallback = function(){
		$('#loading-busy-layer').show()
		$.ajax({
			url: "android_export_check.php",
			method: "POST",
			data: { idx : currentIdx },
		}).done(function(data) {
			var ret = JSON.parse(data);
			$('#loading-busy-layer').hide()
			if(ret["res"]){
				doAndroidExport();
			}
		});
	}
	$('#AOS_Settings').submit();
}
function doAndroidExport(){
	$('#loading-busy-layer').show()
	$.ajax({
		url: "android_export_do.php",
		method: "POST",
  		data: { idx : currentIdx },
	}).done(function(data) {
		$('#loading-busy-layer').hide()
	});
}
function removeProject(){
	$('#removeModal').modal("hide");
	$.ajax({
		url: "remove_builds.php",
		method: "POST",
  		data: { idx : currentIdx },
	}).done(function() {
		document.location.reload();
	});
}
</script>
<div style="float:left">
	<h2>빌드 업로드</h2>
	<div class="box-small" style="width:320px">
		<form id="build_upload" enctype="multipart/form-data" action="upload_builds.php" method="POST">
			<div class="form-group">
				<label for="projName">프로젝트 이름</label>
				<input id="projName" name="projName" class="form-control" type="input" />
			</div>

			<div class="form-group">
				<label for="userfile">Build 폴더</label>
				<input name="userfile" type="file" />
			</div>
			<div class="progress">
				<div class="bar"></div >
				<div class="percent">0%</div >
			</div>
			<div id="status"></div>

			<button type="submit" class="btn btn-primary">업로드</button><br>
			<div style="font-size:9pt;">*프로젝트 내에 있는 build폴더를 압축하여 올려주세요.</div><br>
		</form>
	</div>
</div>

<div style="float:left;margin-left:5px;width:800px">
	<h2>빌드 리스트</h2>
	<div class="box-small">
		<?
		$sql = "SELECT * FROM `pini_console`.`builds` WHERE mb_id='$mb_id' ORDER BY datetime DESC";
		$result = sql_query($sql);
		?>
		<table class="table">
			<thead>
				<tr>
					<th>#</th>
					<th width="200px">프로젝트 명</th>
					<th>용량</th>
					<th>업로드 날짜</th>
					<th>빌드파일</th>
					<th>안드로이드</th>
					<th>아이폰</th>
					<th>삭제</th>
				</tr>
			</thead>
			<tbody>
				<?
				$i=0;
				while($row = sql_fetch_array($result)){
					$i++;
				?>
				<tr class="active">
					<th scope="row"><?=$i?></th>
					<td><?=$row["projname"]?></td>
					<td><?=round($row["capacity"]/1024/1024,2)?>MB</td>
					<td><?=$row["datetime"]?></td>
					<td><button type="button" class="btn btn-primary btn-sm">설정</button></td>
					<td><button type="button" class="btn btn-primary btn-sm" onClick="openAndroidModal(<?=$row["idx"]?>)">설정</button></td>
					<td><button type="button" class="btn btn-primary btn-sm">설정</button></td>
					<td><button type="button" class="btn btn-danger btn-sm" onClick="openDeleteModal(<?=$row["idx"]?>)">삭제</button></td>
				</tr>
				<? } ?>
			</tbody>
		</table>
	</div>
</div>

<div style="clear:both"></div>

<!-- Modal -->
<div class="modal fade" id="removeModal" tabindex="-1" role="dialog" aria-labelledby="removeModalLabel" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
				<h4 class="modal-title" id="removeModalLabel">프로젝트 삭제</h4>
			</div>
			<div class="modal-body">
				해당 프로젝트를 정말로 삭제하시겠습니까?
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-default" data-dismiss="modal">아니오</button>
				<button type="button" class="btn btn-danger" onClick="removeProject()">예</button>
			</div>
		</div>
	</div>
</div>

<!-- Modal -->
<div class="modal fade" id="androidConfigureModal" tabindex="-1" role="dialog" aria-labelledby="androidConfigureModalLabel" aria-hidden="true">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
				<h4 class="modal-title" id="androidConfigureModalLabel">안드로이드 익스포트 정보</h4>
			</div>
			<div class="modal-body">
				<form id="AOS_Settings" enctype="multipart/form-data" action="android_export_save.php" method="POST">
					<input type="hidden" id="AOS_idx" name="AOS_idx" >
					<div class="form-group">
						<label for="AOS_icon">아이콘</label>
						<img id="AOS_icon_display" src="img/export_default_icon.png" style="float:left;width:64px;height:64px;margin-right:10px">
						<input type="file" id="AOS_icon" name="AOS_icon" style="float:left">
						<p class="AOS-icon-help-block">512px * 512px 크기,PNG파일 아이콘을 업로드해주세요. </p>
					</div>
					<div class="form-group">
						<label for="AOS_gameName">게임명</label>
						<input type="email" class="form-control" id="AOS_gameName" name="AOS_gameName" placeholder="설치 시 디스플레이 될 게임이름">
					</div>
					<div class="form-group">
						<label for="AOS_packageName">패키지명</label>
						<input type="email" class="form-control" id="AOS_packageName" name="AOS_packageName" placeholder="앱 고유이름. '.'으로 구분하며 영어만 사용할 수 있음 ex)com.Team_Name.Game_Name">
					</div>
					<div class="form-group">
						<label for="AOS_appVersion">앱 버전</label>
						<input type="email" class="form-control" id="AOS_appVersion" name="AOS_appVersion" placeholder="앱의 버전 '.'으로 구분 ex)0.0.1 ">
					</div>
					<div class="form-group">
						<label for="AOS_keystore">키스토어</label>
						<input type="file" id="AOS_keystore" name="AOS_keystore">
						<p class="AOS-keystore-help-block">사용중인 키스토어가 있을 시 업로드해주세요.</p>
					</div>
					<div class="form-group">
						<label for="AOS_keyPassword">비밀번호</label>
						<input type="password" class="form-control" id="AOS_keyPassword" name="AOS_keyPassword" placeholder="비밀번호를 잃어버리면 구글플레이 업데이트를 할 수 없습니다.">
					</div>
					<button type="button" class="btn btn-primary" id="apkExport" onClick="checkAndroidExport()" >익스포트</button>
					<button type="button" class="btn btn-success" id="apkDownload" onClick="_apkDownload()" >다운로드</button>
				</form>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-default" data-dismiss="modal">닫기</button>
				<button type="button" class="btn btn-warning" onClick="saveAndroidModel()">저장 후 닫기</button>
			</div>
		</div>
	</div>
</div>

<script>
$(function(){
	$(":file").filestyle({icon: false});

	var bar = $('.bar');
	var percent = $('.percent');
	var status = $('#status');
	var projName = $('#projName');
	$('#build_upload').ajaxForm({
		beforeSubmit : function(){
			if(projName.val().length < 3){
				alert("프로젝트 이름은 3자 이상이여야합니다.");
				return false;
			}
			return true;
		},
		beforeSend: function() {
			status.empty();
			var percentVal = '0%';
			bar.width(percentVal)
			percent.html(percentVal);
		},
		uploadProgress: function(event, position, total, percentComplete) {
			var percentVal = percentComplete + '%';
			bar.width(percentVal)
			percent.html(percentVal);
		},
		success: function() {
			var percentVal = '100%';
			bar.width(percentVal)
			percent.html(percentVal);
		},
		complete: function(xhr) {
			var ret = JSON.parse(xhr.responseText)
			status.html(ret["msg"]);
			if(ret["res"] == 1){
				document.location.reload();
			}
		}
	}); 

	$('#AOS_Settings').ajaxForm({
		beforeSubmit : function(){
			if($("#AOS_gameName").val().length <= 0){
				alert("게임이름을 입력해주세요.");
				return false;
			}
			if($("#AOS_packageName").val().length < 5){
				alert("패키지명은 최소 5자입니다.\nex)com.team.game");
				return false;
			}
			if($("#AOS_appVersion").val().length < 3){
				alert("앱버전은 최소 3자입니다.\nex)0.1");
				return false;
			}
			if($("#AOS_keyPassword").val().length <= 8){
				alert("비밀번호는 최소 9자입니다.");
				return false;
			}
			return true;
		},
		beforeSend: function() {
			$('#loading-busy-layer').show();
			$('#androidConfigureModal').modal("hide");
		},
		success: function() {},
		complete: function(xhr) {
			var ret = JSON.parse(xhr.responseText);
			if(ret["icon"] && (ret["iconW"] != 512 || ret["iconH"] != 512 || ret["iconT"] != 3)){
				alert("이미지 크기 512*512가 아니거나 확장자가 png가 아닙니다.");
			}else{
				alert("빌드 정보가 정상적으로 저장되었습니다.");
			}
			$('#loading-busy-layer').hide();
			if(submitCallback)
				submitCallback();
			submitCallback = null;
		}
	}); 
})
</script>

<?php
}else{
	echo "<h2>로그인을 하셔야합니다.</h2>";
}

include_once ('./console.tail.php');
?>

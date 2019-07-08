<?php
# ФУНКЦИЯ КАЛЕНДАРЯ build_cal('prefix'); создает массив переменных в сессии с префиксом в начале (где применяется должно быть session_start();)
# $_SESSION[$pref.'XXX']  Где XXX может быть:
# 3 переменных выбранной даты 2 - текущего календаря 1 - lunix_time 
# _selected_d - изначально не определены. После клика на дату - определяет
# _selected_m
# _selected_y
# _current_m - сразу определены после POST меняются
# _current_y
# _date - дата и время в linux формате
# Пример: Функция build_cal('test'); создаст массив переменных типа $_SESSION["test_selected_d"]

# Навигация
if (isset($_POST["prev"])) {
	$pref = $_POST["pref_name"];
	if ($_SESSION[$pref."_current_m"] == 1) {
		$_SESSION[$pref."_current_y"]--;
		$_SESSION[$pref."_current_m"] = 12;
	}
	else $_SESSION[$pref."_current_m"]--;
	unset($pref);
}
if (isset($_POST["next"])) {
	$pref = $_POST["pref_name"];
	if ($_SESSION[$pref."_current_m"] == 12) {
		$_SESSION[$pref."_current_y"]++;
		$_SESSION[$pref."_current_m"] = 1;
	}
	else $_SESSION[$pref."_current_m"]++;
	unset($pref);
}
# Действие при нажатие на дату
if (isset($_POST["select_day"])) {
	$pref = $_POST["pref_name"];
	$_SESSION[$pref."_selected_d"] = $_POST["select_day"];
	$_SESSION[$pref."_selected_m"] = $_SESSION[$pref."_current_m"];
	$_SESSION[$pref."_selected_y"] = $_SESSION[$pref."_current_y"];
	$_SESSION[$pref."_date"] = mktime(0,0,0,$_SESSION[$pref."_selected_m"],$_SESSION[$pref."_selected_d"],$_SESSION[$pref."_selected_y"]);
	unset($pref);
}
# Сама функция
function build_cal($pref) {
$month_names=array("январь","февраль","март","апрель","май","июнь","июль","август","сентябрь","октябрь","ноябрь","декабрь");
# Добавляем префикс к переменным
$sel_d = $pref."_selected_d";
$sel_m = $pref."_selected_m";
$sel_y = $pref."_selected_y";
$cur_m = $pref."_current_m";
$cur_y = $pref."_current_y";
$prev = $pref."_prev";
$next = $pref."_next";
# Выставляем тукущий месяц календаря 
if (!isset($_SESSION[$cur_m])) $_SESSION[$cur_m] = date("m");
if (!isset($_SESSION[$cur_y])) $_SESSION[$cur_y] = date("Y");
# Другие переменные даты
$month_date_start=mktime(0,0,0,$_SESSION[$cur_m],1,$_SESSION[$cur_y]);
$month_days_count=date("t",$month_date_start);
$month_weekday_start=date("w",$month_date_start);
$month_weekday_end = date("w",$month_date_start+3600*24*$month_days_count-1);
if ($month_weekday_start==0) $month_weekday_start=7;
if ($month_weekday_end==0) $month_weekday_end=7;
$td_in_table = $month_days_count+$month_weekday_start-$month_weekday_end+6;

echo '<form method="POST" action="'.$_SERVER["PHP_SELF"].'">';
echo '<input type="hidden" name="pref_name" value="'.$pref.'">
<table border="0" cellspacing="0" cellpadding="0" id="cal"><tr width="100%">
<td align="left"><input name="prev" type="submit" value="<<"></td>
<td colspan="5" align="center"> '.$month_names[$_SESSION[$cur_m]-1].' '.$_SESSION[$cur_y].' </td>
<td align="right"><input name="next" type="submit" value=">>"></td></tr>';
echo '<tr><td>Пн</td><td>Вт</td><td>Ср</td><td>Чт</td><td>Пт</td><td>Сб</td><td>Вс</td></tr>';
for($d=0;$d<$td_in_table;$d++) {
	if (!($d % 7)) echo "<tr>";
	if ($d+1<$month_weekday_start or $d>$month_days_count+$month_weekday_start-2) {
		echo '<td align="center">&nbsp</td>';
	} else {
		if (isset($_SESSION[$sel_d]) and $_SESSION[$sel_d]==$d+2-$month_weekday_start and $_SESSION[$sel_m]==$_SESSION[$cur_m]) echo '<td align="center"><input class="select_day" name="select_day" type="submit" value="'.($d+2-$month_weekday_start).'"></td>'; 
		else echo '<td align="center"><input name="select_day" type="submit" value="'.($d+2-$month_weekday_start).'"></td>'; 
	}
	if (!(($d+1)% 7) and $d>1) echo "</tr>";
}

echo '</table></form>';
}
?>
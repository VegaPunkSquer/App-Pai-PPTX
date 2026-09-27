import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider with ChangeNotifier {
  bool _isDarkMode = true; // Começa no Escuro por padrão

  bool get isDarkMode => _isDarkMode;

  ThemeProvider() {
    _carregarTema();
  }

  Future<void> _carregarTema() async {
    final prefs = await SharedPreferences.getInstance();
    // Se não tiver nada salvo, assume true (Escuro)
    _isDarkMode = prefs.getBool('vega_is_dark') ?? true;
    notifyListeners();
  }

  Future<void> toggleTheme(bool isDark) async {
    _isDarkMode = isDark;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('vega_is_dark', isDark);
    notifyListeners(); // Grita pro app inteiro mudar de cor na mesma hora!
  }
}
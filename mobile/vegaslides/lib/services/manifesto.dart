import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';

class Manifesto {
  static Map<String, dynamic> _dados = {};

  static Future<void> inicializar() async {
    try {
      // Lê o arquivo gerado pela sua Fábrica direto da raiz
      final String jsonStr = await rootBundle.loadString('vega_manifesto.json');
      _dados = jsonDecode(jsonStr);
    } catch (e) {
      debugPrint("Aviso: vega_manifesto.json não encontrado ou inválido. $e");
    }
  }

  static String get nomeApp => _dados['nome'] ?? 'App VegaTech';
  static int get produtoId => _dados['produto_id_master'] ?? 1;
  static Map<String, dynamic> get planosPrecos => _dados['planos_precos'] ?? {};
}
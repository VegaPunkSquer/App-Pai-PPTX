import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import 'package:vegaslides/services/manifesto.dart';

class AuthProvider with ChangeNotifier {
  String? _token;
  
  // Se tem token, o cara é VIP (tá logado)
  bool get isAuth => _token != null;
  String? get token => _token;

  AuthProvider() {
    _carregarToken();
  }

  // Busca na memória do celular assim que o app abre
  Future<void> _carregarToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('vega_token_master');
    notifyListeners(); // Avisa o app inteiro que o status mudou
  }

  Future<void> fazerLogin(String email, String senha) async {
    final dados = await ApiService.login(email, senha);
    
    if (dados.containsKey('access_token')) {
      _token = dados['access_token'];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('vega_token_master', _token!);
      
      // O RADAR SILENCIOSO: Sem o "1" chumbado!
      final statusPlano = await ApiService.checarMeuPlano(_token!);
      
      await prefs.setBool('vega_saas_padrao', false);
      await prefs.setBool('vega_saas_elite', false);
      await prefs.setBool('vega_byok_ativo', false);

      if (statusPlano['tem_plano_ativo'] == true) {
        final nomePlanoAPI = statusPlano['plano_nome'].toString().toUpperCase();
        final configPlano = Manifesto.planosPrecos[nomePlanoAPI] ?? {};
        final pulseira = configPlano['nivel']?.toString().toUpperCase() ?? 'PADRAO';

        if (pulseira == '3') { // 3 = Pulseira Elite
          await prefs.setBool('vega_saas_elite', true);
          await prefs.setString('vega_license', 'SAAS');
        } else if (pulseira == '1') { // 1 = Pulseira Padrão
          await prefs.setBool('vega_saas_padrao', true);
          await prefs.setString('vega_license', 'SAAS');
        } else if (pulseira == '2') { // 2 = Pulseira BYOK
          await prefs.setBool('vega_byok_ativo', true);
          await prefs.setString('vega_license', 'BYOK');
        } else {
          await prefs.setString('vega_license', pulseira);
        }
      } else {
        await prefs.setString('vega_license', 'FREE');
      }

      notifyListeners();
    }
  }

  Future<void> fazerCadastro(String nome, String email, String senha) async {
    final dados = await ApiService.registrar(nome, email, senha);
    
    if (dados.containsKey('access_token')) {
      _token = dados['access_token'];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('vega_token_master', _token!);
      
      // O RADAR SILENCIOSO: Sem o "1" chumbado!
      final statusPlano = await ApiService.checarMeuPlano(_token!);
      
      await prefs.setBool('vega_saas_padrao', false);
      await prefs.setBool('vega_saas_elite', false);
      await prefs.setBool('vega_byok_ativo', false);

      if (statusPlano['tem_plano_ativo'] == true) {
        final nomePlanoAPI = statusPlano['plano_nome'].toString().toUpperCase();
        final configPlano = Manifesto.planosPrecos[nomePlanoAPI] ?? {};
        final pulseira = configPlano['nivel']?.toString().toUpperCase() ?? 'PADRAO';

        if (pulseira == '3') { // 3 = Pulseira Elite
          await prefs.setBool('vega_saas_elite', true);
          await prefs.setString('vega_license', 'SAAS');
        } else if (pulseira == '1') { // 1 = Pulseira Padrão
          await prefs.setBool('vega_saas_padrao', true);
          await prefs.setString('vega_license', 'SAAS');
        } else if (pulseira == '2') { // 2 = Pulseira BYOK
          await prefs.setBool('vega_byok_ativo', true);
          await prefs.setString('vega_license', 'BYOK');
        } else {
          await prefs.setString('vega_license', pulseira);
        }
      } else {
        await prefs.setString('vega_license', 'FREE');
      }

      notifyListeners();
    }
  }

  Future<void> fazerLogout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('vega_token_master');
    notifyListeners();
  }
}
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:vegaslides/services/manifesto.dart';

class ApiService {
  static const String baseUrl = "https://vegap-masterapp.hf.space";

  static Future<Map<String, dynamic>> login(String email, String senha) async {
    final url = Uri.parse("$baseUrl/auth/app/login");
    
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": email, 
          "senha": senha
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body); // Retorna TUDO que a Nave-Mãe mandou
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'E-mail ou senha incorretos.');
      }
    } catch (e) {
      throw Exception("Falha de conexão com a Nave-Mãe: $e");
    }
  }

  // Busca os avisos globais da Nave-Mãe
  static Future<List<dynamic>> buscarAvisos() async {
    // Usa o nome dinâmico lido do manifesto para puxar os avisos corretos
    final nomeAppEncoded = Uri.encodeComponent(Manifesto.nomeApp);
    final url = Uri.parse("$baseUrl/master/publico/avisos/$nomeAppEncoded");
    try {
      final response = await http.get(url).timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      // Ignora erro silenciosamente para não travar o app
    }
    return [];
  }

  static Future<Map<String, dynamic>> registrar(String nome, String email, String senha) async {
    final url = Uri.parse("$baseUrl/auth/app/registrar");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        // Manda o nome do app dinâmico para a Nave-Mãe
        body: jsonEncode({"nome": nome, "email": email, "senha": senha, "produto": Manifesto.nomeApp}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        final erro = jsonDecode(response.body);
        throw Exception(erro['detail'] ?? "Erro desconhecido ao cadastrar.");
      }
    } catch (e) {
      throw Exception("Falha ao registrar: $e");
    }
  }

  // ==========================================
  // O RADAR SILENCIOSO DO PLANO
  // ==========================================
  static Future<Map<String, dynamic>> checarMeuPlano(String token) async {
    final id = Manifesto.produtoId;
    final url = Uri.parse("$baseUrl/master/pagamentos/$id/meu-status");
    
    try {
      final response = await http.get(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body); // Retorna { "tem_plano_ativo": true/false, "plano_nome": "..." }
      } else {
        return {"tem_plano_ativo": false, "plano_nome": "FREE"};
      }
    } catch (e) {
      return {"tem_plano_ativo": false, "plano_nome": "FREE"};
    }
  }

  // ==========================================
  // COMUNICADORES DA LOJA E CHECKOUT
  // ==========================================
  static Future<Map<String, dynamic>> buscarVitrine(String moeda) async {
    // Usamos o nome do app configurado no seu banco para puxar os preços
    final nomeAppEncoded = Uri.encodeComponent(Manifesto.nomeApp);
    final url = Uri.parse("$baseUrl/master/vitrine/$nomeAppEncoded?moeda=$moeda");
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception("Erro ao carregar a vitrine.");
    } catch (e) {
      throw Exception("Falha de conexão com a loja: $e");
    }
  }

  static Future<Map<String, dynamic>> gerarCheckout(String token, String planoNome, String cupom, String gateway) async {
    final url = Uri.parse("$baseUrl/master/pagamentos/gerar-checkout");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "token": token,
          "produto_id": Manifesto.produtoId, // O ID agora é 100% dinâmico
          "plano_nome": planoNome,
          "cupom": cupom,
          "gateway": gateway
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final erro = jsonDecode(response.body);
        throw Exception(erro['detail'] ?? "Erro desconhecido no checkout");
      }
    } catch (e) {
      throw Exception("Falha ao processar o pagamento: $e");
    }
  }

  static Future<bool> checarStatusPagamento(String cobrancaId) async {
    final url = Uri.parse("$baseUrl/master/pagamentos/checar-status?cobranca_id=$cobrancaId");
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body)['pago'] ?? false;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  // ==========================================
  // FÁBRICA DE APRESENTAÇÕES (NUVEM)
  // ==========================================
  static Future<String> gerarApresentacao(String token, String tema) async {
    final url = Uri.parse("$baseUrl/master/mobile/gerar-apresentacao");
    
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "tema": tema,
          "token": token,
        }),
      ).timeout(const Duration(seconds: 60)); // 60 segundos porque a IA demora pra pensar

      if (response.statusCode == 200) {
        final dados = jsonDecode(response.body);
        return dados['link_download'];
      } else {
        final erro = jsonDecode(response.body);
        throw Exception(erro['detail'] ?? "Erro ao gerar apresentação.");
      }
    } catch (e) {
      throw Exception("Falha de conexão com a IA: $e");
    }
  }
}
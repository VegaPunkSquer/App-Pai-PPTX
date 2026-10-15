import 'dart:convert';
import 'dart:typed_data';
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

  static Future<void> recuperarSenha(String email) async {
    final url = Uri.parse("$baseUrl/auth/app/recuperar-senha");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email}),
      );
      if (response.statusCode != 200 && response.statusCode != 201) {
        final err = jsonDecode(response.body);
        throw Exception(err['detail'] ?? "Erro ao solicitar recuperação de senha.");
      }
    } catch (e) {
      throw Exception("Falha na conexão: $e");
    }
  }

  static Future<void> confirmarRecuperacaoSenha(String email, String codigo, String novaSenha) async {
    final url = Uri.parse("$baseUrl/auth/app/confirmar-recuperacao");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": email,
          "codigo": codigo,
          "nova_senha": novaSenha,
        }),
      );
      if (response.statusCode != 200 && response.statusCode != 201) {
        final err = jsonDecode(response.body);
        throw Exception(err['detail'] ?? "Código inválido ou expirado.");
      }
    } catch (e) {
      throw Exception("Falha ao redefinir senha: $e");
    }
  }

  static Future<Map<String, dynamic>> obterPerfil(String token) async {
    final url = Uri.parse("$baseUrl/auth/app/perfil");
    try {
      final response = await http.get(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return {};
    } catch (e) {
      return {};
    }
  }

  static Future<bool> salvarFotoPerfil(String token, String base64Foto) async {
    final url = Uri.parse("$baseUrl/auth/app/foto");
    try {
      final response = await http.post(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({"foto": base64Foto}),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      return false;
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

  // Busca as notas de atualização (Novidades) da Nave-Mãe
  static Future<Map<String, dynamic>> buscarNovidades() async {
    final id = Manifesto.produtoId;
    final url = Uri.parse("$baseUrl/master/atualizacao/$id?plataforma=mobile");
    try {
      final response = await http.get(url).timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      }
    } catch (e) {
      // Ignora erro silenciosamente
    }
    return {};
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
  // FÁBRICA DE APRESENTAÇÕES (NUVEM - 2 ETAPAS)
  // ==========================================
  static Future<List<dynamic>> planejarApresentacao(String token, String tema) async {
    final url = Uri.parse("$baseUrl/master/mobile/planejar-apresentacao");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "tema": tema,
          "token": token,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final dados = jsonDecode(utf8.decode(response.bodyBytes));
        return dados['slides'] ?? [];
      } else {
        final erro = jsonDecode(utf8.decode(response.bodyBytes));
        throw Exception(erro['detail'] ?? "Erro ao planear a apresentação.");
      }
    } catch (e) {
      throw Exception("Falha de conexão com a IA: $e");
    }
  }

  static Future<Uint8List> compilarApresentacao(String token, List<Map<String, dynamic>> slides) async {
    final url = Uri.parse("$baseUrl/master/mobile/compilar-apresentacao");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "token": token,
          "slides": slides,
        }),
      ).timeout(const Duration(seconds: 120));

      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        final erro = jsonDecode(utf8.decode(response.bodyBytes));
        throw Exception(erro['detail'] ?? "Erro ao compilar o ficheiro PPTX.");
      }
    } catch (e) {
      throw Exception("Falha ao compilar apresentação: $e");
    }
  }

  // Compatibilidade com o HomeScreen durante a transição
  static Future<String> gerarApresentacao(String token, String tema) async {
    final slides = await planejarApresentacao(token, tema);
    if (slides.isEmpty) {
      throw Exception("Nenhum slide foi gerado.");
    }
    return "planejamento_concluido";
  }

  // ==========================================
  // MOTOR GRATUITO: ESTILIZAÇÃO DE PPTX E CONVERSÃO PDF
  // ==========================================
  static Future<Uint8List> processarEstilos({
    required Uint8List arquivoBytes,
    required String nomeArquivo,
    String? corTitulo,
    String? corCorpo,
    String? corFundoCard,
    String? fonteTitulo,
    String? fonteCorpo,
    int escalaImagem = 100,
    int escalaTexto = 0,
    bool exibirBarraLateral = true,
    bool converterPdf = false,
    Uint8List? imagemFundoBytes,
    String? nomeImagemFundo,
  }) async {
    final url = Uri.parse("$baseUrl/master/mobile/processar-estilos");
    final request = http.MultipartRequest("POST", url);

    request.files.add(
      http.MultipartFile.fromBytes('arquivo', arquivoBytes, filename: nomeArquivo),
    );

    if (corTitulo != null && corTitulo.isNotEmpty) {
      request.fields['cor_titulo'] = corTitulo;
    }
    if (corCorpo != null && corCorpo.isNotEmpty) {
      request.fields['cor_corpo'] = corCorpo;
    }
    if (corFundoCard != null && corFundoCard.isNotEmpty) {
      request.fields['cor_fundo_card'] = corFundoCard;
    }
    if (fonteTitulo != null && fonteTitulo.isNotEmpty) {
      request.fields['fonte_titulo'] = fonteTitulo;
    }
    if (fonteCorpo != null && fonteCorpo.isNotEmpty) {
      request.fields['fonte_corpo'] = fonteCorpo;
    }
    request.fields['escala_imagem'] = escalaImagem.toString();
    request.fields['escala_texto'] = escalaTexto.toString();
    request.fields['exibir_barra_lateral'] = exibirBarraLateral.toString();
    request.fields['converter_pdf'] = converterPdf.toString();

    if (imagemFundoBytes != null && nomeImagemFundo != null) {
      request.files.add(
        http.MultipartFile.fromBytes('imagem_fundo', imagemFundoBytes, filename: nomeImagemFundo),
      );
    }

    try {
      final streamedResponse = await request.send().timeout(const Duration(seconds: 120));
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        final erro = jsonDecode(utf8.decode(response.bodyBytes));
        throw Exception(erro['detail'] ?? "Erro ao processar estilos no servidor.");
      }
    } catch (e) {
      throw Exception("Falha de conexão com o processador: $e");
    }
  }
}